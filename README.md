# **Sticker Printing Optimization**
Easily **minimize total printed pages** while meeting sticker demands using **OR-Tools CP-SAT**. This approach helps define **up to N layouts**—each with a limited **capacity**—and decides how many copies of each sticker to include per layout.

## **Problem Overview**
- You have multiple stickers (each identified by a name) with a required demand (i.e., how many copies of that sticker are needed).
- You want to place these stickers into up to a certain number of layouts (printing plates), each layout having a limited capacity (a maximum number of sticker spots).
- For each layout you define, you can print it multiple times, producing as many copies of the included stickers as needed.
- Goal: Minimize the total number of printed pages (i.e., how many times each layout is printed), while meeting or exceeding the demand for each sticker.
- Constraints:
  - Each layout can hold at most layout_capacity stickers in total (sum of copies of all sticker types in that layout).
  You have a maximum of max_layouts layouts you can define.
  - Each sticker’s demand must be met or exceeded by the total prints of the layouts that include it.
  - Every sticker must appear in at least one layout.


## **Key Features**
- **Reduce Printing Costs**: Minimizes the total number of printed pages.
- **Meet or Exceed Demand**: Ensures every sticker’s required amount is fulfilled.
- **Flexible Layouts**: Define up to `max_layouts`, each with configurable `layout_capacity`.
- **Fast Optimization**: Powered by Google’s **OR-Tools CP-SAT** solver.

## **Example output**

```Solver status: FEASIBLE
Used layouts: [0, 1]
Total pages (layouts printed): 6063

Layout 0: printed 1037 times.
  Distribution (sticker_name -> copies_per_page):
    Sticker 7 => 2
    Sticker 11 => 2
    ...

Layout 1: printed 5026 times.
  Distribution (sticker_name -> copies_per_page):
    Sticker 13 => 6
    Sticker 16 => 5
    ...

Demand checks:
  Sticker 13: printed=30156, required=29100, met=True
  Sticker 16: printed=25130, required=24300, met=True
  ...
```

## **Other**
For questions or feedback, open an issue in the repository or email marcin@sobczak.me