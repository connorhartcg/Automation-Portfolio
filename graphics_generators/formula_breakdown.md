**Graphics Generators Formulas**
    **Source Sheet**
        ## Raw data csv from Treez(POS AND INVENTORY SYSTEM) inventory adjustment page
    **Consolidate**
        =UNIQUE(SourceSheet!D:D)
        *- A1 - Provides a list of unique product names from the datasheet*
        =TEXTJOIN(", ", TRUE, FILTER(SourceSheet!H:H, SourceSheet!D:D = A1))
        *- B1 - Pulls all the product barcodes associated with each product*
        =TEXTJOIN(", ", TRUE, FILTER(SourceSheet!J:J, SourceSheet!D:D = A1))
        - C1 - Pulls all inventory barcodes associated with each product (there is a different between product and inventory barcodes.)
        =ARRAYFORMULA(B2:B & ", " & C2:C)
        - D2 - Combines skus from the previous two columns, keeping them separated by commas
        =IFERROR(INDEX(SPLIT($D2, ", "), 1), "")
        - E2 - isolates the first sku from the list
        - F2 - same formula as the prior, but 1 changes to 2. This pattern is repeated 25 times to accommodate the few products that have a lot of batches and skus
        =MAX(FILTER(SourceSheet!N:N, SourceSheet!D:D = A2))
        - AD2 - Finds the highest price out of the datasheet associated with the product in A2; in case there's a duplicate product name that has been misappropriately priced.
        =IFERROR(REGEXEXTRACT(A2, "(INDICA|SATIVA|HYBRID|CBD)"), "")
        - AE2 - Extracts the lineage from the product name
        =IFERROR(INDEX(SourceSheet!C:C, MATCH(A2, SourceSheet!D:D, 0)), "")
        - AF2 - displays the associated brand name
        =TRIM(REGEXREPLACE(REGEXREPLACE(REGEXREPLACE(SUBSTITUTE(SUBSTITUTE(SUBSTITUTE(SUBSTITUTE(SUBSTITUTE(A2, AE2, ""), AF2, ""), AK2, ""), AH2, ""), ": ", ""), "PACK", ""), "(?i)\b(" & TEXTJOIN("|", TRUE, $AN$2:$AN) & ")\b", ""), "\s\d+(\s|$)|^\d+\s", ""))
        - AG2 - Cleans up the product name by removing the lineage, brand name, and any other unwanted text. This is a long formula that uses regex to remove unwanted text.
        =INDEX(SourceSheet!A:A, MATCH(A2, SourceSheet!D:D, 0))
        - AH2 - Pulls the product type from the datasheet
        =INDEX(SourceSheet!K:K, MATCH(A2, SourceSheet!D:D, 0)) & IF(INDEX(SourceSheet!L:L, MATCH(A2, SourceSheet!D:D, 0)) = "GRAMS", "G", "MG")
        - AI2 - Pulls the product weight from the datasheet and appends "G" or "MG" depending on the unit of measure.
        =AD2
        - AJ2 - Pulls the price from earlier in this sheet
        =IF(LEFT(AI2, 1) = "0", SUBSTITUTE(AI2, "0", "", 1), AI2)
        - AK2 - Cleans up the weight by removing the leading zero if it exists.
        =INDEX(SourceSheet!B:B, MATCH(A2, SourceSheet!D:D, 0))
        - AL2 - Pulls the product subtype from the datasheet
        =IFERROR(INDEX(SourceSheet!G:G, MATCH(A2, SourceSheet!D:D, 0)), "")
        - AM2 - Pulls the product tracking number from the datasheet
        -Name Shorteners- in Column AN
        SMALLS
        GUMMIES
        SOLVENTLESS
        ELEMENTS
        BADDER
        PRIVATE RESERVE
        INFUSED
        CRUSHED DIAMOND
        LOLLIS
        MIXED LIGHT
        INDOOR
        ALL-IN-ONE
        CLASSIC
        BLUNT
        CRUSHED DIAMONDS
        DESIGNER
        DISTILLATE
        BY
        GUMMY
        LITTLE FLAVES
        LIVE RESIN
        LIVE ROSIN
        PREMIUM
        BLACK BAG
        GREEN BAG
        PERSY
        TIER 1
        TIER 2
        TIER 3
        TIER 4
        CUREPEN
        SINGLE
        VEGAN
        ALIEN FINGER
        LIQUID DIAMONDS
        JUICE CART
        DIAMONDS
        WHITE BAG
        -Buzzwords- in Column AO
        Relaxing
        Sedating
        Calming
        Tranquil
        Soothing
        Blissful
        Stress Relief
        Balanced
        Euphoric
        Social
        Soothing
        Energizing
        Creative
        Uplifting
        Motivating
        Joyful
        Focused
        Cerebral
        -Special Terms-
        PERSY
        TIER 1
        TIER 2
        TIER 3
        TIER 4
        CUREPEN
        SOLVENTLESS
        MIXED LIGHT
        INDOOR
        ALL-IN-ONE
        LIVE RESIN
        LIVE ROSIN
        BLACK BAG
        GREEN BAG
        WHITE BAG
        INFUSED
        GREY BAG
        10 PACK
        6 PACK
    **TagInput**
        In A2 and below, scan skus from the sales floor.
        =INDEX(Consolidate!$A:$A, FILTER(ROW(Consolidate!$E:$E), EXACT(Consolidate!$E:$E, A2) + EXACT(Consolidate!$F:$F, A2) + EXACT(Consolidate!$G:$G, A2) + EXACT(Consolidate!$H:$H, A2) + EXACT(Consolidate!$I:$I, A2) + EXACT(Consolidate!$J:$J, A2) + EXACT(Consolidate!$K:$K, A2) + EXACT(Consolidate!$L:$L, A2) + EXACT(Consolidate!$M:$M, A2) + EXACT(Consolidate!$N:$N, A2) + EXACT(Consolidate!$O:$O, A2) + EXACT(Consolidate!$P:$P, A2) + EXACT(Consolidate!$Q:$Q, A2) + EXACT(Consolidate!$R:$R, A2) + EXACT(Consolidate!$S:$S, A2) + EXACT(Consolidate!$T:$T, A2) + EXACT(Consolidate!$U:$U, A2) + EXACT(Consolidate!$V:$V, A2) + EXACT(Consolidate!$W:$W, A2) + EXACT(Consolidate!$X:$X, A2) + EXACT(Consolidate!$Y:$Y, A2) + EXACT(Consolidate!$Z:$Z, A2) + EXACT(Consolidate!$AA:$AA, A2) + EXACT(Consolidate!$AB:$AB, A2) + EXACT(Consolidate!$AC:$AC, A2) + EXACT(Consolidate!$AM:$AM, A2)))
        - B2 - Matches the sku or tracking number from A2 to a specific product.
            **New Tag Input**
                =INDEX(Consolidate!AH:AH, MATCH(LOWER(SUBSTITUTE(H2, " ", "")), LOWER(SUBSTITUTE(Consolidate!A:A, " ", "")), 0))
                - G2 - displays the product type associated with the scanned product
                =TagInput!B2
                - H2 - Displays the scanned product name
                =VLOOKUP(H2, Consolidate!A:AJ, 36, FALSE)
                - I2 - Displays the scanned product's OLD/sticker price
                =INDEX(Consolidate!AE:AE, MATCH(LOWER(SUBSTITUTE(H2, " ", "")), LOWER(SUBSTITUTE(Consolidate!A:A, " ", "")), 0))
                - J2 - Displays the lineage
                =INDEX(Consolidate!AF:AF, MATCH(LOWER(SUBSTITUTE(H2, " ", "")), LOWER(SUBSTITUTE(Consolidate!A:A, " ", "")), 0))
                - K2 - Displays the brand
                =INDEX(Consolidate!AG:AG, MATCH(LOWER(SUBSTITUTE(H2, " ", "")), LOWER(SUBSTITUTE(Consolidate!A:A, " ", "")), 0))
                - L2 - Displays the shortened product name of the scanned product
                =J2
                - M2 - Displays the lineage again, this was done because a sequential page is simply going to transpose this information in order.
                =INDEX(Consolidate!AK:AK, MATCH(LOWER(SUBSTITUTE(H2, " ", "")), LOWER(SUBSTITUTE(Consolidate!A:A, " ", "")), 0))
                - N2 - Displays the weight
                =I2
                - O2 - Displays the old price
                =ARRAYFORMULA(IFERROR(
                    INDEX('New Price Data'!J:J, MATCH(1, 
                        (LOWER(K2) = LOWER('New Price Data'!M:M)) * 
                        (LOWER(G2) = LOWER('New Price Data'!O:O)) * 
                        (LOWER(N2) = LOWER('New Price Data'!N:N)) * 
                        (LOWER(Q2) = LOWER('New Price Data'!P:P)) * 
                        IF(R2 = "", 1, IF(REGEXMATCH(LOWER('New Price Data'!Q:Q), LOWER(R2)), 1, 0)), 
                        0)), O2 * 0.7))
                - P2 - Displays the discounted price. At a time we had a sheet with brand price guidelines post discount, before all products in the store were discounted; now all of them are and the math can simply be done in the formula instead of looking up the price
            **NewPriceTagResult**
                This page is simply all of the scanned product values from the prior page across the second row to minimize time that autocrat spends merging this into a word doc. If it was multiple rows, autocrat would create a new word doc for every row, instead of merging the maximum of 40 display tags on one sheet of paper.    
            **NewPrerollCards**
                =VLOOKUP(H2, 'Logo Reference'!H:I, 2, FALSE)
                - C2 - Looks at Lineage to determine background URL
                =INDEX(Consolidate!A:A, FILTER(ROW(Consolidate!E:E), EXACT(Consolidate!E:E, B2) + EXACT(Consolidate!F:F, B2) + EXACT(Consolidate!G:G, B2) + EXACT(Consolidate!H:H, B2) + EXACT(Consolidate!I:I, B2) + EXACT(Consolidate!J:J, B2) + EXACT(Consolidate!K:K, B2) + EXACT(Consolidate!L:L, B2) + EXACT(Consolidate!M:M, B2) + EXACT(Consolidate!N:N, B2) + EXACT(Consolidate!O:O, B2) + EXACT(Consolidate!P:P, B2) + EXACT(Consolidate!Q:Q, B2) + EXACT(Consolidate!R:R, B2) + EXACT(Consolidate!S:S, B2) + EXACT(Consolidate!T:T, B2) + EXACT(Consolidate!U:U, B2) + EXACT(Consolidate!V:V, B2) + EXACT(Consolidate!W:W, B2) + EXACT(Consolidate!X:X, B2) + EXACT(Consolidate!Y:Y, B2) + EXACT(Consolidate!Z:Z, B2) + EXACT(Consolidate!AA:AA, B2) + EXACT(Consolidate!AB:AB, B2) + EXACT(Consolidate!AC:AC, B2)))
                - D2 - Displays product name based on sku in B2
                =IF(LEN(VLOOKUP(D2, Consolidate!A:AG, 33, FALSE)) > 8, IF(LEN(VLOOKUP(D2, Consolidate!A:AG, 33, FALSE)) <= 25, VLOOKUP(D2, Consolidate!A:AG, 33, FALSE), ""), "")
                - E2 - displays the strain name of the product
                =VLOOKUP(D2, Consolidate!A:AH, 32, FALSE)
                - F2 - Displays the brand
                =VLOOKUP(D2, Consolidate!A:AJ, 36, FALSE)
                - G2 - Displays the sticker price
                =VLOOKUP(D2, Consolidate!A:AH, 31, FALSE)
                - H2 - Displays the lineage
                