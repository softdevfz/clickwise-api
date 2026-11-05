# Import a Clickwise product feed into WooCommerce with WP All Import

[Español](wp-all-import.es.md)

This guide describes importing a Clickwise XML feed as WooCommerce **External/Affiliate** products. Their purchase button sends visitors to the seller through the feed's tracked link.

**Validation status:** we have not tested this workflow with Pro. The local test on 2026-09-30 used the free editions and a synthetic file to create and update **Simple** products. It did not validate external products, their purchase button, URL downloads or scheduling. The Pro instructions below are a configuration procedure to verify on a staging site, based on the plugin documentation and the limitations observed in the free editions.

## Prepare the site and feed

- Use a staging copy of your WordPress and WooCommerce site, with a backup before changing import settings.
- For external products, use **WP All Import Pro** and the **WooCommerce Add-On Pro**. URL download and recurring import are also Pro features. Check the supported WordPress, WooCommerce and PHP versions for the editions you install.
- Set the WooCommerce store currency to the feed's currency. Mapping a price does not convert currencies.
- Keep feeds separate: create a separate import for each feed and keep its source and matching identifier consistent.
- Review the Clickwise feed access and program rules at <https://partners.clickwise.net/feeds/guide/>. Affiliate signup is at <https://partners.clickwise.net/en/signup_affiliate/>. Access to a production feed depends on the applicable program approvals.

Use the current signed feed URL supplied for your approved affiliate access. Keep it private: do not put it in public documentation, screenshots, source control or support messages. Preserve purchase links and their parameters unchanged.

### Start with the public sample

Download the fictional XML sample from <https://partners.clickwise.net/feeds/guide/sample.xml>. It illustrates the structure; its purchase links are fictional and do not validate live tracking or purchases.

For a free-edition preview, save the sample and choose **Upload a file**. Use **Simple** products in a staging site for this preview only. That route does not produce an affiliate catalogue. The historical free-edition test used a locally constructed synthetic substitute, not this downloaded public sample.

For **Pro — not tested with Pro**, use the sample URL in **Download a file › From URL** before configuring a private production source.

## Understand the XML and matching identifiers

The repeating record is `item` under `/rss/channel/item`. In the local test, WP All Import displayed namespaced fields with underscores: `g:id` became `g_id`, and `g:price` became `g_price`. Use the names shown in your import's element tree.

| Feed field | WP All Import placeholder | Purpose |
|---|---|---|
| `title` | `{title[1]}` | Product title |
| `description` | `{description[1]}` | Product description |
| `g:id` | `{g_id[1]}` | Offer identifier; use for import matching and the intended SKU mapping |
| `link` | `{link[1]}` | Tracked purchase link in a standard delivery |
| `g:price` | `{g_price[1]}` | Regular price, including the feed currency code |
| `g:sale_price`, when supplied | `{g_sale_price[1]}` | Sale price; check how the installed importer handles an absent value |
| `g:gtin`, when supplied | `{g_gtin[1]}` | Product identifier, preserved as text with leading zeros |
| `g:image_link` | `{g_image_link[1]}` | Main image URL |
| `g:availability` | `{g_availability[1]}` | Availability at the seller |
| `g:product_type`, when supplied | `{g_product_type[1]}` | Category path |

An offer identifier and a GTIN serve different purposes. The offer identifier matches the same offer across imports. A GTIN identifies a product and can be shared by different offers. **Use `{g_id[1]}` as the Unique Identifier; do not match by GTIN or title.**

The intended SKU is also `{g_id[1]}`. Do not replace it with the GTIN. WooCommerce's native GTIN field has a uniqueness constraint; duplicate GTIN handling by WP All Import was not tested. Do not assume it silently leaves the field empty or still creates the product. Test the import log and resulting records with repeated GTINs before using the native GTIN mapping. If needed, evaluate preserving the raw value in a separate custom field such as `_clickwise_gtin`; this option remains untested.

For a standard delivery, map Product URL to `{link[1]}`. If a delivery uses a landing template, `link` can point to your page while `g:clickwise_link` retains the tracked purchase link. In that case, inspect the file and use `{g_clickwise_link[1]}` only when that element is present and is the intended tracked destination. Do not modify the signed source URL or remove tracking parameters to change this behavior.

## Create the import

### Source — Pro, not tested with Pro

Open **All Import › New Import › Download a file › From URL**, enter the public sample URL and download it. Choose **WooCommerce Products** as the import target, then **Set Up Import**.

Check that the preview records correspond to `item` elements. If the detected structure is wrong, review the record selector and the installed version's documentation before continuing. The local free-edition run detected the records automatically; editing the record selector was not tested.

### Product type and mappings — Pro, not tested with Pro

In **WooCommerce Add-On › Product Type**, choose **External/Affiliate product**. The free add-on showed this choice but disabled its external fields. It did not execute an external import.

| Destination | Mapping or setting |
|---|---|
| Title | `{title[1]}` |
| Description | `{description[1]}` |
| Product URL | `{link[1]}`, subject to the landing-template check above |
| Button text | `Buy at seller` or an equivalent label in your site's language |
| Regular Price | `{g_price[1]}` |
| Sale Price, if present | `{g_sale_price[1]}`; verify absent-value handling |
| Remove currency symbols from price | Enabled; verify the resulting numeric price and store currency |
| Product status | Draft while reviewing the result |

Price normalization was observed with Simple products in the free-edition test. Its behavior for External/Affiliate products with Pro remains untested. Avoid applying price adjustments that make the displayed price differ from the seller's offer.

**SKU and GTIN in Pro need confirmation.** The intended mappings are SKU = `{g_id[1]}` and, where suitable after duplicate testing, GTIN = `{g_gtin[1]}`. These mappings were tested in the free edition's Simple product Inventory screen. The official Pro import guide says that External/Affiliate selection hides the Inventory and Shipping tabs. Do not expect that screen to be available for external products. Verify the supported SKU and GTIN controls in your installed Pro version before completing the import; this guide does not prescribe writing WooCommerce internal metadata as a workaround. Unique Identifier is configured separately under Import Settings.

### Images and categories — Pro external flow not tested

In **Images**, select **Download images hosted elsewhere** and map `{g_image_link[1]}`. Choose the featured-image option and, where offered, **Search through the Media Library › Match image by URL**. Test with the public sample before relying on downloads from seller image hosts.

A public demo image downloaded and was reused during the historical Simple-product test. Downloads from a production seller's image host were not tested. Check image warnings in the import history and review the resulting media.

If `g:product_type` exists, inspect its category path before mapping it to WooCommerce categories. Alternatively choose a fixed category for this import. Check the hierarchy separator rather than assuming it matches your feed.

## Configure matching and updates

In **Import Settings**, choose **Create new Products for each record in this import file** and enter **`{g_id[1]}` as Unique Identifier**. Replace an auto-detected expression if it includes a title or other changing value. Keep this expression unchanged on subsequent runs of the same import.

Enable creating newly present records and updating changed records. Use **Choose which data to update** when you maintain descriptions, categories or other editorial content manually. Select only the fields the feed should control, including the intended price, purchase link and availability mappings. Review image replacement options as well; replacing all data can remove and recreate existing attachments.

The free-edition Simple test updated existing records without creating new product records when the identifier was unchanged. This is historical evidence, not a test of the Pro external flow.

Keep automatic removal disabled until you have verified availability, filtering and missing-record handling on staging.

## Handle seller availability

In the WooCommerce 9.9.5 external product class reviewed for the original guide, external products force stock status to **In stock**, disable stock management and disallow backorders. Therefore a WooCommerce stock label is not evidence that an external offer is available at the seller. Recheck this behavior with your installed WooCommerce version.

Do not map `g:availability` to external-product stock quantity or assume WooCommerce's “hide out of stock” option will hide unavailable external offers. Preserve the feed value in an attribute or a separate custom field such as `_clickwise_availability` and configure your theme to display it. **That mapping and theme behavior have not been tested with Pro.**

The feed values are `in_stock`, `out_of_stock`, `preorder` and `backorder`. Show the seller's supplied status without inventing a shipping date or quantity.

### Optional filter and missing-record policy — not tested with Pro

If you only want available offers, evaluate **Create Filters › g_availability › equals › in_stock**. A filter can make previously imported offers absent from the next import's selected records. Without an appropriate missing-record policy, they may remain published with stale data.

Evaluate **Remove or modify products that are not present in this import file › Change status to Draft**, scoped only to products managed by this import. Avoid deletion while validating the workflow. Test an offer becoming unavailable, disappearing and returning, and verify both matching and publication status. The filter, drafting of absent records and restoration of returning offers were not tested; do not assume returning offers republish automatically.

Before acting on missing records, check download and parsing logs and confirm feed access remains valid. A failed download and a valid file with missing offers need different investigation. Do not assume the importer protects every failure case; verify its behavior on staging.

## Run and verify — Pro external flow not tested

Review the import summary and choose **Confirm & Run Import** on staging. Open **All Import › Manage Imports › History Logs** and investigate errors before publishing.

Verify the product type, price and currency, intended SKU, GTIN leading zeros where applicable, images and seller availability. Check the resulting product page and shop listing. Inspect the purchase button's destination and confirm it preserves the feed's tracked link. The fictional sample cannot validate a live purchase or commission attribution.

Show an affiliate disclosure on the site and mark outbound affiliate links with `rel="sponsored nofollow noopener"`. Check the rendered link in your theme; this guide has not tested a theme change or a Pro purchase button.

Run the same import again with unchanged matching settings and inspect whether existing records are updated without duplication. Review manually curated fields to ensure they were preserved. Validate missing-record behavior separately before enabling it for a production feed.

## Refreshing and replacing the source — Pro, not tested with Pro

For scheduling, use a **Download from URL** or **Use existing file** source. A manually uploaded file is not the scheduling source described by WP All Import. Configure either its optional **Automatic Scheduling** service or server cron following the official instructions for the installed version.

Manual scheduling uses separate **trigger** and **processing** URLs: the trigger marks an import as due and processing performs the work. Copy the URLs privately from the import's **Scheduling Options** and follow the vendor's recommended configuration. They contain authorization data; do not paste them into this guide or public logs. We did not install or execute cron, Automatic Scheduling or a Pro refresh.

When Clickwise supplies a replacement signed source URL, open the existing import's **Settings › Import File**, replace the source privately, save, and verify a manual run on staging. Keep the matching identifier unchanged. Replacing a signed URL in Pro was not tested. The historical free-edition test only replaced an uploaded synthetic source file.

If refreshes fail, review source access and program eligibility, the current signed URL, the import log and scheduling configuration. Do not publish old prices as if they were newly checked.

## Troubleshooting

| Symptom | Check |
|---|---|
| External fields disabled | Confirm that both required Pro editions are installed and active. We did not bypass free-edition restrictions. |
| `{g:price[1]}` returns nothing | Use the placeholder names in the element tree; the local test used `{g_price[1]}`. |
| Price is text or incorrect | Check currency stripping, decimal parsing and store currency; inspect the stored result. |
| Images missing | Check the history log and whether your server can access the image host. |
| GTIN conflict | Keep matching by `g:id`; test native GTIN uniqueness and read the importer error instead of assuming a particular outcome. |
| Unavailable offer still labelled In stock | Use seller availability data separately; external-product stock behavior is different. |
| Duplicate products after refresh | Check the import identity and Unique Identifier before running again. |

## What was tested

On **2026-09-30**, a local sandbox used **WordPress 6.8.3, WooCommerce 9.9.5, WP All Import free 4.1.1 and WooCommerce Add-On free 1.5.5**. These are historical test versions, not a statement of current releases or compatibility requirements.

The test uploaded a locally constructed synthetic file as Simple products, mapped title, description, price, SKU and GTIN, preserved GTIN leading zeros, and used `{g_id[1]}` for matching. An update through the existing import preserved product records, downloaded a public demo image and reused it. The test products were then manually set to Draft.

**Not tested:** Pro installation and external import; external purchase button; URL download or signed-URL replacement; scheduling; production seller image hosts; duplicate GTIN handling; availability display; filters and missing-record drafting or restoration. The public sample URL was not the source used in that historical execution.

## Official references

- Clickwise feed access and program rules: <https://partners.clickwise.net/feeds/guide/>
- Clickwise fictional XML sample: <https://partners.clickwise.net/feeds/guide/sample.xml>
- WP All Import add-on and Pro features: <https://wordpress.org/plugins/woocommerce-xml-csv-product-import/>
- WooCommerce import configuration: <https://www.wpallimport.com/documentation/how-to-import-woocommerce-products-csv-xml/>
- Source types: <https://www.wpallimport.com/documentation/download-a-file-or-use-existing-file/>
- Scheduling: <https://www.wpallimport.com/documentation/cron/>
- Unique Identifier: <https://www.wpallimport.com/documentation/define-unique-identifier-correctly/>
- Missing records: <https://www.wpallimport.com/documentation/remove-data-missing-from-the-import-file/>
