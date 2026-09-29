"""Presentation pass. No prices, measurements or stock are invented here."""
import re


def refine(path, body):
    if path == 'index.html':
        # Keep the editorial feature, but make the supporting cards a compact row.
        body = body.replace('DESCUBRIR NOVEDADES', 'EXPLORAR EL CATÁLOGO').replace('href="#novedades"', 'href="catalogo/index.html"')
        body = body.replace('SELECCIÓN ACTUAL / 001', 'EL ARCHIVO / SELECCIÓN ACTUAL')
        body = body.replace('RECIÉN<br>LLEGADAS', 'EN EL<br>ARCHIVO')
        body = body.replace('EL ARCHIVO DÉCADA / 2004', 'LA FORMA DÉCADA')
    if path.startswith('productos/'):
        actions = re.search(r'<div class="detail-actions">.*?</div>', body).group(0)
        # The old purchase link loops back to the same product on the live site.
        actions = re.sub(r'<a class="button outline detail-buy".*?</a>', '', actions)
        actions = re.sub(r'data-link="[^"]+"', f'data-link="../../{path}"', actions)
        body = body.replace(re.search(r'<div class="detail-actions">.*?</div>', body).group(0), '')
        body = body.replace('<p class="detail-description">', actions + '<p class="detail-description">', 1)
        body = body.replace('AÑADIR A MI BOLSA', 'AÑADIR A LA BOLSA')
        body = re.sub(r'<section class="measure-panel">(.*?)</section>',
                      r'<details class="measure-panel" open><summary>Medidas y ajuste <span aria-hidden="true">＋</span></summary><div class="measure-content">\1</div></details>', body)
        body = body.replace('Las medidas de esta pieza figuran en las fotografías de la ficha original.', 'Las medidas de esta pieza están pendientes de confirmar.')
        body = re.sub(r'<a href="https://decada.store/productos/[^\"]+" target="_blank" rel="noopener noreferrer">Consultar ficha ↗</a>', '<a href="../../contacto/index.html">Preguntar por las medidas ↗</a>', body)
        body = body.replace('SIGUE EXPLORANDO', 'OTRA PIEZA, OTRA HISTORIA')
        body = body.replace('<h2>OTRAS PIEZAS', '<h2>TAMBIÉN EN EL ARCHIVO')
    if path == 'carrito/index.html':
        body = '''<section class="page-hero compact bag-hero"><div class="crumb"><a href="../index.html">INICIO</a> / BOLSA</div><p class="eyebrow">DÉCADA / TU SELECCIÓN</p><h1>MI BOLSA<span>.</span></h1><p>Las piezas que has elegido. Cada una, una sola vez.</p></section><section class="section bag-page"><div><div id="bag-items" aria-live="polite"></div><div id="bag-empty"><span class="empty-mark" aria-hidden="true">D.</span><h2>TODAVÍA POR DESCUBRIR.</h2><p>Tu próxima pieza está en el archivo.</p><a class="button pink" href="../catalogo/index.html">EXPLORAR EL CATÁLOGO <span>↗</span></a></div><a class="under-link bag-continue" href="../catalogo/index.html">SEGUIR EXPLORANDO ↗</a></div><aside class="bag-summary" data-bag-summary hidden><p>RESUMEN / DÉCADA</p><h2>TU SELECCIÓN.</h2><div class="summary-line"><span>Prendas</span><span data-bag-quantity>0</span></div><div class="summary-line total"><span>Subtotal</span><strong data-bag-total>0,00 €</strong></div><p>Envío no incluido. Guardar una pieza en la bolsa no la reserva.</p><a class="button pink" href="../contacto/index.html">CONSULTAR MI SELECCIÓN <span>↗</span></a><p class="bag-disclaimer">Confirma la disponibilidad y las condiciones con DÉCADA antes de pagar.</p></aside></section>'''
    return body
