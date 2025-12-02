import os
import base64
import gradio as gr

# ---------- Paths / assets ----------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def load_image_data_uri(rel_path):
    """
    Read an image file under this repo and return a data: URI
    that <img src="..."> can use in Gradio / browser.
    """
    full_path = os.path.join(BASE_DIR, rel_path)
    with open(full_path, "rb") as f:
        data = f.read()
    b64 = base64.b64encode(data).decode("ascii")
    # assume PNG; if your files are JPEG, change the mime type
    return f"data:image/png;base64,{b64}"

SHIP_IMG = load_image_data_uri("images/ship.png")
ISLAND_IMG = load_image_data_uri("images/island.png")
TREASURE_IMG = load_image_data_uri("images/treasure.png")

# Audio files (local filepaths)
WATER_SOUND = os.path.join(BASE_DIR, "sounds", "water.mp3")
ARR_SOUND = os.path.join(BASE_DIR, "sounds", "arr.mp3")
TREASURE_SOUND = os.path.join(BASE_DIR, "sounds", "treasurefound.mp3")


# ---------- Core binary search logic (step-based) ----------

def parse_array(array_str):
    """
    Parse a comma/space separated string into a sorted list of ints.
    Raises ValueError on bad input.
    """
    if not array_str.strip():
        raise ValueError("Array cannot be empty.")

    # Split on commas or whitespace
    parts = [p for chunk in array_str.split(",") for p in chunk.split()]
    nums = [int(p) for p in parts]

    # For binary search, we sort ascending
    nums.sort()
    return nums


def render_visual(state):
    """
    Build an HTML visualization of:
    - islands (array values) using island.png
    - lo, hi bounds (text labels)
    - mid (ship.png)
    - found island (treasure.png)
    """
    if state is None or "array" not in state:
        return "<p>Click <b>Start / Reset</b> to begin.</p>"

    arr = state["array"]
    lo = state["lo"]
    hi = state["hi"]
    mid = state.get("mid", None)
    target = state["target"]
    found_index = state.get("found_index", None)
    step = state["step"]
    finished = state["finished"]

    # bigger padding so the large icons have room
    base_style = (
        "display:inline-block;margin:6px;padding:8px 10px;"
        "text-align:center;font-family:monospace;"
    )

    islands_html = []

    for i, val in enumerate(arr):
        style = base_style

        # Grey out islands outside the current search window
        if i < lo or i > hi:
            island_opacity = 0.35
        else:
            island_opacity = 1.0

        # Top row labels/icons
        top_bits = []

        # lo / hi text labels – a bit bigger
        lh_labels = []
        if i == lo:
            lh_labels.append("L")
        if i == hi:
            lh_labels.append("H")
        if lh_labels:
            top_bits.append(
                "<div style='font-size:14px;margin-bottom:4px;'>"
                + " ".join(lh_labels)
                + "</div>"
            )

        # ship and treasure images (larger)
        icon_row = ""
        icons = []
        if i == mid:
            icons.append(
                f"<img src='{SHIP_IMG}' alt='ship' "
                "style='width:40px;height:40px;object-fit:contain;margin-right:4px;'/>"
            )
        if i == found_index:
            icons.append(
                f"<img src='{TREASURE_IMG}' alt='treasure' "
                "style='width:40px;height:40px;object-fit:contain;'/>"
            )
        if icons:
            icon_row = (
                "<div style='margin-bottom:4px;height:44px;'>"
                + "".join(icons)
                + "</div>"
            )
        else:
            icon_row = "<div style='margin-bottom:4px;height:44px;'></div>"

        top_bits.append(icon_row)

        label_top = "".join(top_bits)

        # Island image itself (larger)
        island_img = (
            f"<img src='{ISLAND_IMG}' alt='island' "
            f"style='width:80px;height:80px;object-fit:contain;opacity:{island_opacity};'/>"
        )

        # Index + value text – slightly bigger
        label_bottom = (
            f"<div style='margin-top:4px;font-size:14px;'>[{i}] = {val}</div>"
        )

        island_div = f"<div style='{style}'>{label_top}{island_img}{label_bottom}</div>"
        islands_html.append(island_div)

    header = f"<h3>Step {step}</h3>"
    sub = f"<p>Target: <b>{target}</b> | lo = {lo}, hi = {hi}, mid = {mid}</p>"

    # make result text much larger
    if finished:
        if found_index is not None:
            status = (
                "<p style='color:green;font-size:32px;font-weight:bold;margin-top:20px;'>"
                f"Treasure found at index {found_index} (value={arr[found_index]}).</p>"
            )
        else:
            status = (
                "<p style='color:red;font-size:32px;font-weight:bold;margin-top:20px;'>"
                "Treasure not found in these islands.</p>"
            )
    else:
        status = "<p>Click <b>Next step</b> to move the ship.</p>"

    return header + sub + "".join(islands_html) + status


def start_search(array_str, target):
    """
    Initialize state for a new binary search run.
    """
    try:
        arr = parse_array(array_str)
    except ValueError as e:
        err_html = f"<p style='color:red;'>Input error: {e}</p>"
        # no sound on error
        return err_html, "Please fix the input and press Start again.", None, None

    if len(arr) == 0:
        err_html = "<p style='color:red;'>Array cannot be empty.</p>"
        return err_html, "Please provide at least one number.", None, None

    lo = 0
    hi = len(arr) - 1

    state = {
        "array": arr,
        "target": int(target),
        "lo": lo,
        "hi": hi,
        "mid": None,
        "step": 0,
        "finished": False,
        "found_index": None,
    }

    visual = render_visual(state)
    explanation = (
        "Array has been parsed and sorted.\n\n"
        f"- Islands (values): {arr}\n"
        f"- Target treasure value: {target}\n"
        "- We'll now do binary search: at each step, the ship sails to the middle island, "
        "compares, and then we discard half the remaining islands."
    )

    # No sound on initialization
    return visual, explanation, None, state


def next_step(state):
    """
    Perform one step of binary search and update the state.
    Returns (visual, explanation, sound_path, state).
    """
    if state is None or "array" not in state:
        html = "<p style='color:red;'>No active search. Click <b>Start / Reset</b> first.</p>"
        return html, "No state: please initialize the search first.", None, state

    if state["finished"]:
        visual = render_visual(state)
        explain = "Search is already finished. Press Start / Reset to try a new example."
        # no additional sound once finished
        return visual, explain, None, state

    arr = state["array"]
    target = state["target"]
    lo = state["lo"]
    hi = state["hi"]
    step = state["step"] + 1

    # If window is already invalid, mark not found
    if lo > hi:
        state["finished"] = True
        state["step"] = step
        state["mid"] = None
        visual = render_visual(state)
        explain = "Search window collapsed (lo > hi). Target is not in the array."
        # play "arr" when we confirm treasure not found
        return visual, explain, ARR_SOUND, state

    # Standard binary search mid
    mid = (lo + hi) // 2
    val = arr[mid]

    state["mid"] = mid
    state["step"] = step

    if val == target:
        # found treasure
        state["finished"] = True
        state["found_index"] = mid
        visual = render_visual(state)
        explain = (
            f"Step {step}:\n"
            f"- Ship sails to island index {mid} with value {val}.\n"
            "- Value matches the target, so this island has the treasure.\n"
            "- Search stops here."
        )
        # play treasure sound once
        return visual, explain, TREASURE_SOUND, state

    elif val < target:
        # discard left half including mid
        old_lo = lo
        lo = mid + 1
        state["lo"] = lo
        state["hi"] = hi
        visual = render_visual(state)
        explain = (
            f"Step {step}:\n"
            f"- Ship sails to island index {mid} with value {val}.\n"
            f"- {val} < {target}, so the treasure must be on the RIGHT side.\n"
            f"- We discard islands from index {old_lo} up to {mid}.\n"
            f"- New search window: lo = {lo}, hi = {hi}."
        )
        # water sound for a normal non-treasure step
        return visual, explain, WATER_SOUND, state

    else:
        # val > target: discard right half including mid
        old_hi = hi
        hi = mid - 1
        state["lo"] = lo
        state["hi"] = hi
        visual = render_visual(state)
        explain = (
            f"Step {step}:\n"
            f"- Ship sails to island index {mid} with value {val}.\n"
            f"- {val} > {target}, so the treasure must be on the LEFT side.\n"
            f"- We discard islands from index {mid} up to {old_hi}.\n"
            f"- New search window: lo = {lo}, hi = {hi}."
        )
        # water sound for a normal non-treasure step
        return visual, explain, WATER_SOUND, state


# ---------- Helper: generate arrays from range + parity ----------

def generate_array_from_range(start, end, mode):
    """
    Generate a comma-separated string of ints between start and end (inclusive),
    filtered by parity mode: 'Even', 'Odd', or 'Both'.
    """
    try:
        start = int(start)
        end = int(end)
    except (TypeError, ValueError):
        return "1, 2, 3, 4, 5, 6, 7, 8, 9, 10"  # fallback

    if end <= start:
        # Simple guard: if bad range, just return start
        return str(start)

    if mode == "Even":
        first = start if start % 2 == 0 else start + 1
        nums = list(range(first, end + 1, 2))
    elif mode == "Odd":
        first = start if start % 2 != 0 else start + 1
        nums = list(range(first, end + 1, 2))
    else:  # "Both"
        nums = list(range(start, end + 1))

    return ", ".join(str(x) for x in nums)


# ---------- Gradio UI ----------

# ---------- Gradio UI ----------

with gr.Blocks(title="Binary Search – Treasure Islands") as demo:
    gr.Markdown(
        """
# Binary Search — Treasure Islands

Use the controls below to generate a row of islands (sorted numbers) or type your own array.  
Then set a target treasure value, click **Start / Reset**, and step through the binary search with **Next step**.
"""
    )

    with gr.Row():
        with gr.Column():
            gr.Markdown("### Island Generator (optional)")
            range_start = gr.Number(
                label="Start value (inclusive)",
                value=1,
                precision=0,
            )
            range_end = gr.Number(
                label="End value (inclusive, > start)",
                value=10,   # default upper bound 10
                precision=0,
            )
            parity_mode = gr.Radio(
                label="Include which numbers?",
                choices=["Both", "Even", "Odd"],
                value="Both",
            )
            generate_button = gr.Button("Generate islands from range")

        with gr.Column():
            gr.Markdown("### Array and Target")
            array_input = gr.Textbox(
                label="Islands (array of numbers)",
                value="1, 2, 3, 4, 5, 6, 7, 8, 9, 10",  # default 1–10
                placeholder="Example: 1, 2, 3, 4, 5",
            )
            target_input = gr.Number(
                label="Treasure value (target)",
                value=7,      # default target 7
                precision=0,
            )

    # Buttons for controlling the search
    start_button = gr.Button("Start / Reset")
    step_button = gr.Button("Next step")

    visual_output = gr.HTML(label="Islands View")
    explanation_output = gr.Markdown(label="Step Explanation")

    # Big spacer so audio is far below everything else
    gr.Markdown("<div style='height:400px'></div>")

    # Audio output: visually reachable only if you scroll way down
    sound_output = gr.Audio(
        label="Audio (sound effects)",
        autoplay=True,
        interactive=False,
        visible=True,   # visible, but far away
    )

    # Internal state object for the search
    search_state = gr.State()

    # Generate array from range -> updates the array_input textbox
    generate_button.click(
        fn=generate_array_from_range,
        inputs=[range_start, range_end, parity_mode],
        outputs=array_input,
    )

    # Initialize / reset search
    start_button.click(
        fn=start_search,
        inputs=[array_input, target_input],
        outputs=[visual_output, explanation_output, sound_output, search_state],
    )

    # Next binary-search step
    step_button.click(
        fn=next_step,
        inputs=[search_state],
        outputs=[visual_output, explanation_output, sound_output, search_state],
    )

if __name__ == "__main__":
    demo.launch()
