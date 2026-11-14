import json, unittest, hashlib
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).parents[1]))
from preview_renderer import build, OUT, PAGES
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

class PreviewQA(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  build(); cls.pw=sync_playwright().start()
  cls.browser=cls.pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 @classmethod
 def tearDownClass(cls): cls.browser.close();cls.pw.stop()
 def test_contract_all_facts_visible(self):
  files=['01-four-training-stages.html','02-next-token-prediction.html']
  for data,name in zip(PAGES,files):
   soup=BeautifulSoup((OUT/name).read_text(encoding='utf-8'),'html.parser')
   for fact in data['facts']:
    holder=soup.select_one(f'[data-fact-id="{fact["id"]}"]')
    self.assertIsNotNone(holder,fact['id']); t=holder.get_text(' ',strip=True)
    self.assertIn(fact['title'],t);self.assertIn(fact['desc'],t);self.assertIn(fact['extra'],t)
    self.assertGreater(len(t),75)
   self.assertEqual(len(soup.select('details.q')),3)
   self.assertEqual(len(soup.select('.check button[data-index]')),3)
   for a in soup.select('a[href$=".html"]'):
    self.assertTrue((OUT/a.get('href')).exists(),a.get('href'))
 def test_real_browser_interactions(self):
  for file,idx in [('01-four-training-stages.html',1),('02-next-token-prediction.html',2)]:
   for width in (390,1280):
    page=self.browser.new_page(viewport={'width':width,'height':900})
    page.set_content((OUT/file).read_text(encoding="utf-8"))
    self.assertGreater(page.locator('[data-fact-id]').count(),7)
    self.assertFalse(page.locator('details.q').first.evaluate('(e)=>e.open'))
    page.locator('details.q summary').first.focus();page.keyboard.press('Enter')
    self.assertTrue(page.locator('details.q').first.evaluate('(e)=>e.open'))
    correct=PAGES[idx-1]['check']['correct']
    page.locator(f'.check button[data-index="{correct}"]').click()
    self.assertIn('正确',page.locator('.feedback').inner_text())
    if idx==1:
     page.locator('[data-scenario="format"]').click()
     self.assertIn('JSON',page.locator('#scenario-output').inner_text())
    else:
     page.locator('#p-slider').evaluate('(e)=>{e.value="70";e.dispatchEvent(new Event("input",{bubbles:true}))}')
     self.assertEqual(page.locator('#loss').inner_text(),'0.357')
     self.assertEqual(page.locator('#p-beijing').inner_text(),'70%')
    page.locator('#reset').click()
    self.assertEqual(page.locator('.feedback').inner_text(),'')
    self.assertFalse(page.locator('details.q').first.evaluate('(e)=>e.open'))
    if idx==1:self.assertIn('领域基础',page.locator('#scenario-output').inner_text())
    else:self.assertEqual(page.locator('#p-display').inner_text(),'0.12')
    self.assertFalse(page.evaluate('document.documentElement.scrollWidth > window.innerWidth+3'))
    if width==1280:
     ss=OUT/('qa-page-'+str(idx)+'.png');page.screenshot(path=str(ss),full_page=True)
    page.close()
 def test_js_disabled_core(self):
  for file in ('01-four-training-stages.html','02-next-token-prediction.html'):
   page=self.browser.new_page(java_script_enabled=False)
   page.set_content((OUT/file).read_text(encoding="utf-8"))
   self.assertEqual(page.locator('[data-fact-id]').count(),8)
   self.assertIn('来源',page.locator('header').inner_text())
   page.locator('details.q summary').first.click()
   self.assertTrue(page.locator('details.q').first.evaluate('(e)=>e.open'))
   page.close()
if __name__=='__main__':unittest.main()
