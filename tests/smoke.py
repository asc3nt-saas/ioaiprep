"""Browser smoke checks. Requires Python Playwright and Chromium."""
from playwright.sync_api import sync_playwright, expect
import os
import json

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH', '/usr/bin/chromium'), args=['--no-sandbox'])
    page = browser.new_page(viewport={'width': 1440, 'height': 1100})
    errors = []
    page.on('pageerror', lambda e: errors.append(str(e)))
    page.goto(os.environ.get('APP_URL', 'http://127.0.0.1:5173'))
    assert page.locator('.card').count() == 6
    page.get_by_role('button', name='Report an item', exact=True).click()
    form = page.locator('form')
    form.get_by_label('Title', exact=False).fill('Test calculator')
    form.get_by_label('Description', exact=False).fill('Silver calculator with a blue sticker')
    form.get_by_label('Location', exact=False).fill('Room 301')
    form.get_by_label('Telegram username', exact=False).fill('@student_test')
    page.get_by_role('button', name='Add listing', exact=True).click()
    assert page.locator('.card').count() == 7
    page.reload()
    assert page.locator('.card').count() == 7
    page.get_by_label('Search items').fill('blue sticker')
    assert page.locator('.card').count() == 1
    page.get_by_label('Category filter').select_option('Clothing')
    assert page.locator('.card').count() == 0
    page.get_by_label('Category filter').select_option('Electronics')
    page.get_by_label('Status filter').select_option('found')
    assert page.locator('.card').count() == 0
    page.get_by_label('Status filter').select_option('lost')
    page.get_by_role('button', name='View Test calculator', exact=True).click()
    assert page.get_by_role('link', name='Contact @student_test on Telegram').get_attribute('href') == 'https://t.me/student_test'
    page.get_by_role('button', name='Edit', exact=True).click()
    page.locator('form').get_by_label('Title', exact=False).fill('Test scientific calculator')
    page.get_by_role('button', name='Save changes').click()
    page.get_by_role('button', name='View Test scientific calculator').click()
    page.get_by_role('button', name='Mark as returned').click()
    expect(page.locator('.detail-badge')).to_have_text('returned')
    page.get_by_role('button', name='Close dialog').click()
    page.get_by_label('Status filter').select_option('returned')
    page.get_by_role('button', name='View Test scientific calculator').click()
    page.get_by_role('button', name='Delete', exact=True).click()
    page.get_by_role('button', name='Cancel', exact=True).click()
    page.get_by_role('button', name='View Test scientific calculator').click()
    page.get_by_role('button', name='Delete', exact=True).click()
    page.get_by_role('button', name='Delete listing', exact=True).click()
    assert page.locator('.card').count() == 0
    page.get_by_role('button', name='Reset filters').first.click()
    page.get_by_role('button', name='Clear sample listings').click()
    page.get_by_role('button', name='Clear samples', exact=True).click()
    page.reload()
    assert page.locator('.card').count() == 0
    page.get_by_role('button', name='Switch to dark theme').click()
    page.reload()
    assert page.locator('html').get_attribute('data-theme') == 'dark'
    page.get_by_role('button', name='Report an item', exact=True).click()
    form = page.locator('form')
    form.get_by_label('Title', exact=False).fill('Photo test')
    form.get_by_label('Description', exact=False).fill('A photographed item')
    form.get_by_label('Location', exact=False).fill('Library')
    page.locator('input[type=file]').set_input_files({'name':'bad.txt','mimeType':'text/plain','buffer':b'bad'})
    assert page.get_by_text('Choose a JPG, PNG, or WebP photo.').is_visible()
    # Generate an image via Chromium's canvas, then exercise real file compression.
    data = page.evaluate('''() => { const c=document.createElement('canvas');c.width=2000;c.height=1200;const x=c.getContext('2d');x.fillStyle='teal';x.fillRect(0,0,2000,1200);return c.toDataURL('image/png').split(',')[1]; }''')
    import base64
    page.locator('input[type=file]').set_input_files({'name':'photo.png','mimeType':'image/png','buffer':base64.b64decode(data)})
    page.get_by_role('button', name='Add listing', exact=True).click()
    stored = page.evaluate("JSON.parse(localStorage.getItem('sps-lost-found-v1'))")
    assert stored[0]['photo'].startswith('data:image/jpeg')
    assert len(stored[0]['photo']) < 1500000
    # Simulate quota exhaustion: listing and form must remain intact.
    page.get_by_role('button', name='Report an item', exact=True).click()
    form = page.locator('form')
    form.get_by_label('Title', exact=False).fill('Unsaved item')
    form.get_by_label('Description', exact=False).fill('Should not persist')
    form.get_by_label('Location', exact=False).fill('Courtyard')
    page.evaluate("() => { window.originalSetItem=Storage.prototype.setItem;Storage.prototype.setItem=function(){throw new DOMException('Full','QuotaExceededError')}; }")
    page.get_by_role('button', name='Add listing', exact=True).click()
    assert page.locator('[role=alert]').filter(has_text='Could not save').count() == 1
    assert page.locator('form').is_visible()
    assert page.evaluate("JSON.parse(localStorage.getItem('sps-lost-found-v1')).length") == 1
    page.evaluate('() => { Storage.prototype.setItem=window.originalSetItem; }')
    page.get_by_role('button', name='Close dialog').click()
    page.get_by_role('button', name='Switch to light theme').click()
    page.set_viewport_size({'width':390,'height':844})
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
    page.screenshot(path='/tmp/lost-found-mobile.png', full_page=True)
    page.set_viewport_size({'width':1440,'height':1100})
    page.evaluate("localStorage.removeItem('sps-lost-found-v1')")
    page.reload()
    page.locator('.card').first.evaluate('(el) => Promise.all(el.getAnimations().map(a => a.finished))')
    page.screenshot(path='/tmp/lost-found-desktop.png', full_page=True)
    assert not errors, errors
    print('PASS: first-visit samples, add/reload, search, category/status filters, details/contact, edit, return, delete/cancel, clear samples persistence, theme persistence, photo validation/compression, storage failure, mobile overflow, no JS errors')
    browser.close()
