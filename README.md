# Binary Search - Treasure Islands

An interactive Gradio website that visualizes the binary search algorithm as a pirate ship sailing between islands to find a hidden treasure chest.

## Name

**Misha Shubin**

## Algorithm Name

**Binary Search (Visualized with Treasure Islands)**

## Demo video/gif/screenshot of test

First View Loaded In:
![loadingin](images/initialss.png)

Mid Binary Search:
![midsearch](images/midsearchss.png)

Treasure Found:
![treasurefound](images/treasurefoundss.png)

Treasure Not Found: 
![treasurenotfound](images/treasurenotfoundss.png)

Sound Effects:
![soundeffectshowcase](images/soundeffectshowcase.png)
I wanted to add sound effects in the background but autoplay requires a visible audio element so I pushed down the main content instead of fully hiding it.

## Problem Breakdown & Computational Thinking

### Decomposition: What smaller steps form your chosen algorithm?
Smaller steps which form the binary search site

- Parse Input
    - Read array as comma and space separated string
    - Convert to 'List[int]' and sort by ascending
    - Read target value as 'int'

- Initialize Search State 
    - lo = 0 and hi is len(array) - 1
    - mid = none, step = 0, finished = False and found_index = none
    - Store everything in a state dictionary type setup that gradio passes between calls

- Single Search Step 
    - If lo > hi then mark treasure not found and stop
    - Compute mid
    - Compare mid with target
        - If equal mark found and stop
        - If less move lo = mid + 1
        - If more move hi = mid - 1

- Visual & Audio Updates
    - Be able to have audio done for every step such as when treasure is found or not found
    - Return proper visuals and sound effects
    - Connect buttons to core functions of binary search 

### Pattern Recognition: How does it repeatedly reach, compare, or swap values?

- Recognizes array is sorted
- Repeats the divide and conquer pattern:
    - Always jump to the middle index between lo and hi
    - Compare mid to target
    - Discard the half the remaining search space
- The same pattern runs for every step until:
    - A match is found
    - lo > hi then target does not exist within array

- Visual Reptition
    - Ship always moves to the middle island
    - Islands outside the current window are faded out

### Abstraction: Which details of the process should be shown to the user and how to show it, and which details should be discarded (i.e., not shown)?

- Shown to the user
    - Island row
    - Pointers 
    - Status/Explanations
    - Audio

- Hidden from the user
    - Code for image display and audio autoplay in background
    - UI internals of Gradio 

### Algorithm Design: How will input → processing → output flow to and from the user? Including the use of the graphical user interface (GUI). Note you are free to choose the datatypes and structures of input (e.g., integer and list or string and linked list, etc.) as long as it is explicitly stated. Include this plan as a short section with a flowchart diagram in your README.

![Binary Search Flowchart](images/finalprojectflowchart.png)

**Data types / structures**

- Array (islands)
    - GUI: text (Gradio Textbox with comma/space separated integers)
    - Internal: 'List[int]' after parsing and sorting

- Target (treasure value)
    - GUI: numeric (Gradio 'Number')
    - Internal: 'int'

- Search state (single dictionary)  
  - `state = { "array": List[int], "target": int, "lo": int, "hi": int, "mid": Optional[int], "step": int, "finished": bool, "found_index": Optional[int] }`

- Generator inputs
    - `range_start: int`, `range_end: int`, `mode: str ("Both" | "Even" | "Odd")`.  
    - Output: a generated comma-separated string that populates the array textbox.


## Steps to Run

### Locally on VSCode

1. Clone the repo: https://github.com/mishaSH07/Binary-Search-Treasure-Islands/tree/main
2. Open in VSCode
3. Create a virtual environment
3. Install dependencies: pip install -r requirements.txt
4. Run the app: app.py
5. Open the local Gradio URL shown in the terminal (typically http://127.0.0.1:7860/).

### On Hugging Face

1. Just visit the link: https://huggingface.co/spaces/MishaShubin/Binary-Search-Treasure-Islands

## Hugging Face Link

[Binary Search Treasure Islands]
(https://huggingface.co/spaces/MishaShubin/Binary-Search-Treasure-Islands)

## Author & Acknowledgment

Author: Misha Shubin
Course: CISC 121 Final Project
Algorithm Used: Binary Search

AI Usage Disclosure:
- ChatGPT Level 4 was used to for:
    - Help design gradio interface for step by step visuals and audio cues
    - Assist with the state dictionary 
    - All generated code was reviewed, tested and integrated manually into the final project
