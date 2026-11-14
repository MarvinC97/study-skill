#!/usr/bin/env python3
"""Actual Chromium/Playwright smoke test for the BUNDLED example interaction.
Does not imply future generated HTML has been tested.
"""
from pathlib import Path
from shutil import which
from playwright.sync_api import sync_playwright
p=Path(__file__).resolve().parents[1]/'examples/agent-loop-interactive.html'
with sync_playwright() as t:
    browser_path=which('chromium') or which('chromium-browser') or which('google-chrome')
    browser=t.chromium.launch(headless=True,**({'executable_path':browser_path} if browser_path else {}))
    page=browser.new_page(viewport={'width':390,'height':844})
    page.set_content(p.read_text(encoding="utf-8"), wait_until="load")
    assert 'Tool Result 已写入 Context' in page.locator('#result').inner_text()
    page.get_by_role('button',name='改变条件').click()
    assert 'Tool Result 缺失' in page.locator('#result').inner_text()
    page.get_by_role('button',name='重置').click()
    assert 'Tool Result 已写入 Context' in page.locator('#result').inner_text()
    assert page.locator('details').count()>=2
    page.locator('details').first.locator('summary').focus()
    page.keyboard.press('Enter')
    assert page.locator('details').first.get_attribute('open') is not None
    assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth + 2'), 'Mobile horizontal overflow'
    print('PASS: Chromium runtime toggling, reset, keyboard reveal, mobile width')
    browser.close()
