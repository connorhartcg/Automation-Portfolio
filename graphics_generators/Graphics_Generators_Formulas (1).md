# Graphics Generators Formulas

## Source Sheet
### Raw data CSV from Treez (POS AND INVENTORY SYSTEM) inventory adjustment page

## Consolidate

```excel
=UNIQUE(SourceSheet!D:D)
```
- **A1** – Provides a list of unique product names from the datasheet.

```excel
=TEXTJOIN(", ", TRUE, FILTER(SourceSheet!H:H, SourceSheet!D:D = A1))
```
- **B1** – Pulls all the product barcodes associated with each product.

```excel
=TEXTJOIN(", ", TRUE, FILTER(SourceSheet!J:J, SourceSheet!D:D = A1))
```
- **C1** – Pulls all inventory barcodes associated with each product (there is a difference between product and inventory barcodes).

```excel
=ARRAYFORMULA(B2:B & ", " & C2:C)
```
- **D2** – Combines SKUs from the previous two columns, keeping them separated by commas.

```excel
=IFERROR(INDEX(SPLIT($D2, ", "), 1), "")
```
- **E2** – Isolates the first SKU from the list.

- **F2–AC2** – Same formula as E2, changing the index from 1 to 2, and so on, to extract additional SKUs.

```excel
=MAX(FILTER(SourceSheet!N:N, SourceSheet!D:D = A2))
```
- **AD2** – Finds the highest price from the datasheet associated with the product in A2.

```excel
=IFERROR(REGEXEXTRACT(A2, "(INDICA|SATIVA|HYBRID|CBD)"), "")
```
- **AE2** – Extracts the lineage from the product name.

```excel
=IFERROR(INDEX(SourceSheet!C:C, MATCH(A2, SourceSheet!D:D, 0)), "")
```
- **AF2** – Displays the associated brand name.

```excel
=TRIM(REGEXREPLACE(...))
```
- **AG2** – Cleans up the product name by removing the lineage, brand name, and other text using nested regex.

```excel
=INDEX(SourceSheet!A:A, MATCH(A2, SourceSheet!D:D, 0))
```
- **AH2** – Pulls the product type.

```excel
=INDEX(SourceSheet!K:K, MATCH(A2, SourceSheet!D:D, 0)) & IF(INDEX(SourceSheet!L:L, MATCH(A2, SourceSheet!D:D, 0)) = "GRAMS", "G", "MG")
```
- **AI2** – Pulls the product weight and appends the unit.

```excel
=AD2
```
- **AJ2** – Price.

```excel
=IF(LEFT(AI2, 1) = "0", SUBSTITUTE(AI2, "0", "", 1), AI2)
```
- **AK2** – Cleans weight by removing leading zero.

```excel
=INDEX(SourceSheet!B:B, MATCH(A2, SourceSheet!D:D, 0))
```
- **AL2** – Pulls the product subtype.

```excel
=IFERROR(INDEX(SourceSheet!G:G, MATCH(A2, SourceSheet!D:D, 0)), "")
```
- **AM2** – Product tracking number.

### Name Shorteners (Column AN)
```
SMALLS, GUMMIES, SOLVENTLESS, ELEMENTS, BADDER, PRIVATE RESERVE, INFUSED, CRUSHED DIAMOND,
LOLLIS, MIXED LIGHT, INDOOR, ALL-IN-ONE, CLASSIC, BLUNT, CRUSHED DIAMONDS, DESIGNER,
DISTILLATE, BY, GUMMY, LITTLE FLAVES, LIVE RESIN, LIVE ROSIN, PREMIUM, BLACK BAG,
GREEN BAG, PERSY, TIER 1, TIER 2, TIER 3, TIER 4, CUREPEN, SINGLE, VEGAN, ALIEN FINGER,
LIQUID DIAMONDS, JUICE CART, DIAMONDS, WHITE BAG
```

### Buzzwords (Column AO)
```
Relaxing, Sedating, Calming, Tranquil, Soothing, Blissful, Stress Relief, Balanced, Euphoric,
Social, Energizing, Creative, Uplifting, Motivating, Joyful, Focused, Cerebral
```

### Special Terms
```
PERSY, TIER 1, TIER 2, TIER 3, TIER 4, CUREPEN, SOLVENTLESS, MIXED LIGHT, INDOOR,
ALL-IN-ONE, LIVE RESIN, LIVE ROSIN, BLACK BAG, GREEN BAG, WHITE BAG, INFUSED,
GREY BAG, 10 PACK, 6 PACK
```

## TagInput

- In A2 and below, scan SKUs from the sales floor.

```excel
=INDEX(Consolidate!$A:$A, FILTER(ROW(Consolidate!$E:$E), ...))
```
- **B2** – Matches the SKU or tracking number to a product.

## New Tag Input

```excel
=INDEX(Consolidate!AH:AH, MATCH(LOWER(SUBSTITUTE(H2, " ", "")), LOWER(SUBSTITUTE(Consolidate!A:A, " ", "")), 0))
```
- **G2** – Displays product type.

```excel
=TagInput!B2
```
- **H2** – Product name.

```excel
=VLOOKUP(H2, Consolidate!A:AJ, 36, FALSE)
```
- **I2** – Old/sticker price.

```excel
=INDEX(Consolidate!AE:AE, MATCH(...))
```
- **J2** – Lineage.

```excel
=INDEX(Consolidate!AF:AF, MATCH(...))
```
- **K2** – Brand.

```excel
=INDEX(Consolidate!AG:AG, MATCH(...))
```
- **L2** – Shortened name.

```excel
=J2
```
- **M2** – Lineage.

```excel
=INDEX(Consolidate!AK:AK, MATCH(...))
```
- **N2** – Weight.

```excel
=I2
```
- **O2** – Old price.

```excel
=ARRAYFORMULA(IFERROR(INDEX(...), O2 * 0.7))
```
- **P2** – Discounted price.

## NewPriceTagResult

- Transposes all product info from previous sheet across one row to speed up Autocrat merges. Reduces PDF generation overhead.