# Importar un feed de productos de Clickwise en WooCommerce con WP All Import

[English](wp-all-import.md)

Esta guía describe cómo importar un feed XML de Clickwise como productos **External/Affiliate** de WooCommerce. Su botón de compra lleva al visitante al comercio mediante el enlace con tracking del feed.

**Estado de validación:** no probamos este flujo con Pro. El ensayo local del 2026-09-30 usó las ediciones gratuitas y un archivo sintético para crear y actualizar productos **Simple**. No validó productos externos, su botón de compra, la descarga desde URL ni la programación. Las instrucciones Pro siguientes son un procedimiento de configuración que debe verificarse en staging, basado en la documentación del plugin y en las limitaciones observadas en las ediciones gratuitas.

## Preparar el sitio y el feed

- Usa una copia de staging de tu sitio WordPress y WooCommerce, con respaldo antes de cambiar los ajustes de importación.
- Para productos externos, usa **WP All Import Pro** y **WooCommerce Add-On Pro**. La descarga desde URL y la importación recurrente también son funciones Pro. Comprueba las versiones de WordPress, WooCommerce y PHP compatibles con las ediciones que instales.
- Configura WooCommerce con la moneda del feed. Mapear un precio no convierte monedas.
- Mantén separados los feeds: crea una importación independiente por feed y conserva su origen e identificador de coincidencia.
- Revisa el acceso a feeds y las reglas de los programas de Clickwise en <https://partners.clickwise.net/feeds/guide/>. El registro de afiliados está en <https://partners.clickwise.net/en/signup_affiliate/>. El acceso a un feed de producción depende de las aprobaciones aplicables de los programas.

Usa la URL firmada vigente entregada para tu acceso de afiliado aprobado. Mantenla privada: no la pongas en documentación pública, capturas, control de versiones ni mensajes de soporte. Conserva intactos los enlaces de compra y sus parámetros.

### Empezar con la muestra pública

Descarga la muestra XML ficticia desde <https://partners.clickwise.net/feeds/guide/sample.xml>. Ilustra la estructura; sus enlaces de compra son ficticios y no validan tracking ni compras reales.

Para explorar con la edición gratuita, guarda la muestra y elige **Upload a file**. Usa productos **Simple** en staging solo para esta exploración. Ese recorrido no crea un catálogo de afiliados. El ensayo gratuito histórico utilizó un sustituto sintético construido en local, no esta muestra pública descargada.

Para **Pro — no probado con Pro**, usa la URL de la muestra en **Download a file › From URL** antes de configurar un origen privado de producción.

## Entender el XML y los identificadores de coincidencia

El registro repetido es `item`, bajo `/rss/channel/item`. En el ensayo local, WP All Import mostró los campos con namespace usando guiones bajos: `g:id` pasó a `g_id`, y `g:price` a `g_price`. Usa los nombres del árbol de elementos de tu importación.

| Campo del feed | Marcador de WP All Import | Uso |
|---|---|---|
| `title` | `{title[1]}` | Título del producto |
| `description` | `{description[1]}` | Descripción del producto |
| `g:id` | `{g_id[1]}` | Identificador de oferta; úsalo para coincidencias y como mapeo previsto de SKU |
| `link` | `{link[1]}` | Enlace de compra con tracking en una entrega estándar |
| `g:price` | `{g_price[1]}` | Precio regular, incluido el código de moneda del feed |
| `g:sale_price`, si se proporciona | `{g_sale_price[1]}` | Precio rebajado; comprueba cómo maneja el importador instalado un valor ausente |
| `g:gtin`, si se proporciona | `{g_gtin[1]}` | Identificador de producto, conservado como texto con ceros iniciales |
| `g:image_link` | `{g_image_link[1]}` | URL de la imagen principal |
| `g:availability` | `{g_availability[1]}` | Disponibilidad en el comercio |
| `g:product_type`, si se proporciona | `{g_product_type[1]}` | Ruta de categoría |

El identificador de oferta y el GTIN tienen funciones distintas. El identificador de oferta permite reconocer la misma oferta entre importaciones. El GTIN identifica un producto y puede compartirse entre ofertas distintas. **Usa `{g_id[1]}` como Unique Identifier; no busques coincidencias por GTIN ni por título.**

El SKU previsto también es `{g_id[1]}`. No lo reemplaces por el GTIN. El campo GTIN nativo de WooCommerce exige unicidad; no se probó cómo maneja WP All Import los GTIN duplicados. No asumas que deja el campo vacío sin avisar o que crea igualmente el producto. Prueba el historial y los registros resultantes con GTIN repetidos antes de usar el mapeo nativo. Si hace falta, evalúa conservar el valor original en un custom field independiente, como `_clickwise_gtin`; esta opción sigue sin probarse.

En una entrega estándar, mapea Product URL a `{link[1]}`. Si una entrega usa una plantilla de landing, `link` puede apuntar a tu página y `g:clickwise_link` conservar el enlace de compra con tracking. En ese caso, inspecciona el archivo y usa `{g_clickwise_link[1]}` solo cuando exista y sea el destino con tracking previsto. No modifiques la URL firmada de origen ni elimines parámetros de tracking para cambiar este comportamiento.

## Crear la importación

### Origen — Pro, no probado con Pro

Abre **All Import › New Import › Download a file › From URL**, introduce la URL de la muestra pública y descárgala. Elige **WooCommerce Products** como destino y después **Set Up Import**.

Comprueba que los registros de la vista previa correspondan a elementos `item`. Si la estructura detectada es incorrecta, revisa el selector de registros y la documentación de la versión instalada antes de continuar. El ensayo gratuito local detectó los registros automáticamente; no se probó editar el selector.

### Tipo de producto y mapeos — Pro, no probado con Pro

En **WooCommerce Add-On › Product Type**, elige **External/Affiliate product**. El add-on gratuito mostraba esa opción, pero deshabilitaba sus campos externos. No ejecutó una importación externa.

| Destino | Mapeo o ajuste |
|---|---|
| Title | `{title[1]}` |
| Description | `{description[1]}` |
| Product URL | `{link[1]}`, sujeto a la comprobación de la plantilla de landing anterior |
| Button text | `Comprar en el comercio` o una etiqueta equivalente en el idioma del sitio |
| Regular Price | `{g_price[1]}` |
| Sale Price, si está presente | `{g_sale_price[1]}`; verifica el manejo de valores ausentes |
| Remove currency symbols from price | Activado; verifica el precio numérico resultante y la moneda de la tienda |
| Estado del producto | Draft mientras revisas el resultado |

La normalización del precio se observó con productos Simple en el ensayo gratuito. Su comportamiento para productos External/Affiliate con Pro sigue sin probarse. Evita ajustes de precio que hagan que el precio mostrado difiera de la oferta del comercio.

**SKU y GTIN en Pro requieren confirmación.** Los mapeos previstos son SKU = `{g_id[1]}` y, cuando corresponda tras probar duplicados, GTIN = `{g_gtin[1]}`. Estos mapeos se probaron en la pantalla Inventory de productos Simple de la edición gratuita. La guía oficial de importación Pro indica que External/Affiliate oculta las pestañas Inventory y Shipping. No esperes que esa pantalla esté disponible para productos externos. Verifica los controles admitidos de SKU y GTIN en tu versión Pro instalada antes de completar la importación; esta guía no prescribe escribir metadatos internos de WooCommerce como alternativa. Unique Identifier se configura por separado en Import Settings.

### Imágenes y categorías — flujo externo Pro sin probar

En **Images**, selecciona **Download images hosted elsewhere** y mapea `{g_image_link[1]}`. Elige la opción de imagen destacada y, si está disponible, **Search through the Media Library › Match image by URL**. Prueba con la muestra pública antes de depender de descargas desde los servidores de imágenes de los comercios.

En el ensayo histórico de productos Simple se descargó y reutilizó una imagen pública de demostración. No se probaron descargas desde el servidor de imágenes de un comercio de producción. Revisa las advertencias del historial y los archivos multimedia resultantes.

Si existe `g:product_type`, inspecciona su ruta antes de mapearla a categorías de WooCommerce. También puedes elegir una categoría fija para esta importación. Comprueba el separador jerárquico en lugar de asumir que coincide con el feed.

## Configurar coincidencias y actualizaciones

En **Import Settings**, elige **Create new Products for each record in this import file** e introduce **`{g_id[1]}` como Unique Identifier**. Reemplaza una expresión autodetectada si incluye el título u otro valor cambiante. Mantén esta expresión en las siguientes ejecuciones de la misma importación.

Activa la creación de registros nuevos y la actualización de registros modificados. Usa **Choose which data to update** si mantienes a mano descripciones, categorías u otro contenido editorial. Selecciona solo los campos que deba controlar el feed, incluidos los mapeos previstos de precio, enlace de compra y disponibilidad. Revisa también las opciones de reemplazo de imágenes; reemplazar todos los datos puede eliminar y recrear adjuntos existentes.

El ensayo gratuito de productos Simple actualizó registros existentes sin crear nuevos registros de producto cuando se conservó el identificador. Es evidencia histórica, no una prueba del flujo externo Pro.

Mantén desactivadas las bajas automáticas hasta verificar en staging la disponibilidad, los filtros y el manejo de registros ausentes.

## Manejar la disponibilidad del comercio

En la clase de producto externo de WooCommerce 9.9.5 revisada para la guía original, los productos externos fuerzan el estado a **In stock**, desactivan la gestión de stock y no admiten backorders. Por tanto, la etiqueta de stock de WooCommerce no demuestra que una oferta externa esté disponible en el comercio. Comprueba este comportamiento con la versión de WooCommerce instalada.

No mapees `g:availability` a la cantidad de stock de productos externos ni asumas que la opción de WooCommerce para ocultar agotados esconderá las ofertas externas no disponibles. Conserva el valor del feed en un atributo o en un custom field independiente, como `_clickwise_availability`, y configura tu tema para mostrarlo. **Ese mapeo y el comportamiento del tema no se probaron con Pro.**

Los valores del feed son `in_stock`, `out_of_stock`, `preorder` y `backorder`. Muestra el estado entregado por el comercio sin inventar fechas de envío ni cantidades.

### Filtro opcional y política de ausentes — no probados con Pro

Si solo quieres ofertas disponibles, evalúa **Create Filters › g_availability › equals › in_stock**. Un filtro puede dejar ofertas importadas fuera de los registros seleccionados en la siguiente ejecución. Sin una política de ausentes adecuada, pueden seguir publicadas con datos desactualizados.

Evalúa **Remove or modify products that are not present in this import file › Change status to Draft**, limitado a productos gestionados por esta importación. Evita borrar mientras validas el recorrido. Prueba una oferta que deja de estar disponible, desaparece y regresa; verifica las coincidencias y el estado de publicación. No se probaron el filtro, el paso de ausentes a borrador ni la restauración de ofertas que regresan; no asumas que se republican automáticamente.

Antes de actuar sobre registros ausentes, revisa los historiales de descarga y lectura del archivo y confirma que el acceso al feed siga vigente. Una descarga fallida y un archivo válido con ofertas ausentes requieren investigaciones distintas. No asumas que el importador protege todos los casos de fallo; verifica su comportamiento en staging.

## Ejecutar y verificar — flujo externo Pro sin probar

Revisa el resumen y elige **Confirm & Run Import** en staging. Abre **All Import › Manage Imports › History Logs** e investiga los errores antes de publicar.

Verifica el tipo de producto, precio y moneda, SKU previsto, ceros iniciales del GTIN cuando corresponda, imágenes y disponibilidad del comercio. Revisa la página de producto y el listado de tienda resultantes. Inspecciona el destino del botón de compra y confirma que conserve el enlace con tracking del feed. La muestra ficticia no puede validar una compra real ni la atribución de comisión.

Muestra un aviso de la relación de afiliación en el sitio y marca los enlaces salientes de afiliados con `rel="sponsored nofollow noopener"`. Comprueba el enlace que genera tu tema; esta guía no probó un cambio de tema ni un botón de compra Pro.

Ejecuta de nuevo la misma importación con los ajustes de coincidencia intactos y comprueba si actualiza los registros existentes sin duplicarlos. Revisa que se conserve el contenido mantenido a mano. Valida por separado el manejo de registros ausentes antes de activarlo con un feed de producción.

## Actualizar y reemplazar el origen — Pro, no probado con Pro

Para programar ejecuciones, usa un origen **Download from URL** o **Use existing file**. Un archivo subido manualmente no es el origen programable que describe WP All Import. Configura el servicio opcional **Automatic Scheduling** o cron del servidor siguiendo las instrucciones oficiales de la versión instalada.

La programación manual utiliza URL separadas de **trigger** y **processing**: trigger marca la importación como pendiente y processing realiza el trabajo. Copia las URL de forma privada desde **Scheduling Options** y sigue la configuración recomendada por el proveedor. Contienen datos de autorización; no las pegues en esta guía ni en historiales públicos. No instalamos ni ejecutamos cron, Automatic Scheduling ni una actualización Pro.

Cuando Clickwise entregue una URL firmada de reemplazo, abre **Settings › Import File** de la importación existente, cambia el origen de forma privada, guarda y verifica una ejecución manual en staging. Conserva el identificador de coincidencia. No se probó reemplazar una URL firmada en Pro. El ensayo gratuito histórico solo reemplazó un archivo sintético subido.

Si fallan las actualizaciones, revisa el acceso al origen y la elegibilidad del programa, la URL firmada vigente, el historial y la configuración de programación. No publiques precios antiguos como si estuvieran recién comprobados.

## Resolver problemas

| Síntoma | Comprobación |
|---|---|
| Campos externos deshabilitados | Confirma que las ediciones Pro requeridas estén instaladas y activas. No se eludieron las restricciones de la edición gratuita. |
| `{g:price[1]}` no devuelve nada | Usa los nombres del árbol de elementos; el ensayo local usó `{g_price[1]}`. |
| Precio como texto o incorrecto | Revisa la eliminación de moneda, el separador decimal y la moneda de la tienda; inspecciona el resultado guardado. |
| Faltan imágenes | Revisa el historial y si tu servidor puede acceder al servidor de imágenes. |
| Conflicto de GTIN | Conserva las coincidencias por `g:id`; prueba la unicidad nativa del GTIN y lee el error del importador en lugar de asumir un resultado concreto. |
| Oferta no disponible marcada In stock | Usa por separado la disponibilidad del comercio; el stock de productos externos se comporta de otra manera. |
| Productos duplicados tras actualizar | Comprueba la identidad de la importación y Unique Identifier antes de volver a ejecutar. |

## Qué se probó

El **2026-09-30**, un sandbox local usó **WordPress 6.8.3, WooCommerce 9.9.5, WP All Import gratuito 4.1.1 y WooCommerce Add-On gratuito 1.5.5**. Son versiones históricas del ensayo, no una afirmación sobre las versiones vigentes ni los requisitos de compatibilidad.

El ensayo subió un archivo sintético construido en local como productos Simple, mapeó título, descripción, precio, SKU y GTIN, conservó los ceros iniciales del GTIN y usó `{g_id[1]}` para las coincidencias. Una actualización desde la importación existente conservó los registros de producto, descargó una imagen pública de demostración y la reutilizó. Después se pasaron los productos de ensayo a Draft de forma manual.

**Sin probar:** instalación Pro e importación externa; botón de compra externo; descarga desde URL o reemplazo de URL firmada; programación; servidores de imágenes de comercios de producción; manejo de GTIN duplicados; visualización de disponibilidad; filtros y paso de ausentes a borrador o restauración. La URL de la muestra pública no fue el origen usado en ese ensayo histórico.

## Referencias oficiales

- Acceso a feeds y reglas de los programas de Clickwise: <https://partners.clickwise.net/feeds/guide/>
- Muestra XML ficticia de Clickwise: <https://partners.clickwise.net/feeds/guide/sample.xml>
- Add-on de WP All Import y funciones Pro: <https://wordpress.org/plugins/woocommerce-xml-csv-product-import/>
- Configuración de importación WooCommerce: <https://www.wpallimport.com/documentation/how-to-import-woocommerce-products-csv-xml/>
- Tipos de origen: <https://www.wpallimport.com/documentation/download-a-file-or-use-existing-file/>
- Programación: <https://www.wpallimport.com/documentation/cron/>
- Unique Identifier: <https://www.wpallimport.com/documentation/define-unique-identifier-correctly/>
- Registros ausentes: <https://www.wpallimport.com/documentation/remove-data-missing-from-the-import-file/>
