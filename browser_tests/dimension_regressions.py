"""Dimension layout: real routes and content, HTTPS fixtures, no publisher requests."""
from copy import deepcopy
from pathlib import Path
import json
import os
import ssl
import subprocess
import tempfile
import threading
import unittest
from playwright.sync_api import sync_playwright, expect
import responsive_smoke as fixtures
from agenda_regressions import event


class DimensionRegressions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tls=tempfile.TemporaryDirectory()
        cert,key=(Path(cls.tls.name)/name for name in ('cert.pem','key.pem'))
        subprocess.run(['openssl','req','-x509','-newkey','rsa:2048','-nodes','-days','1','-keyout',str(key),'-out',str(cert),'-subj','/CN=localhost'],check=True,capture_output=True)
        cls.server=fixtures.ThreadingHTTPServer(('127.0.0.1',0),fixtures.QuietHandler)
        tls=ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER);tls.load_cert_chain(str(cert),str(key))
        cls.server.socket=tls.wrap_socket(cls.server.socket,server_side=True)
        cls.base=f'https://127.0.0.1:{cls.server.server_port}/'
        threading.Thread(target=cls.server.serve_forever,daemon=True).start()
        cls.driver=sync_playwright().start()
        engine=os.environ.get('RADAR_TEST_ENGINE','chromium');options={'headless':True}
        if engine=='chromium' and os.environ.get('RADAR_CHROMIUM_EXECUTABLE'):options['executable_path']=os.environ['RADAR_CHROMIUM_EXECUTABLE']
        cls.browser=getattr(cls.driver,engine).launch(**options)

    @classmethod
    def tearDownClass(cls):
        cls.browser.close();cls.driver.stop();cls.server.shutdown();cls.server.server_close();cls.tls.cleanup()

    def setUp(self):
        self.context=self.browser.new_context(viewport={'width':1440,'height':1000},service_workers='block',ignore_https_errors=True)
        self.context.route('**/*',lambda r:r.continue_() if r.request.url.startswith(self.base) else r.abort())
        self.page=self.context.new_page();self.errors=[]
        self.page.on('pageerror',lambda error:self.errors.append(str(error)))
        self.page.route('**/data/**',fixtures.make_route)
        self.page.goto(self.base+'#inicio')
        self.page.wait_for_function('() => state.ready')

    def tearDown(self):
        self.assertFalse(self.errors)
        self.context.close()

    def test_destinations_are_separate_and_agenda_is_reloadable(self):
        expect(self.page.locator('#dashboardView')).to_be_visible()
        expect(self.page.locator('#agendaSection')).to_be_hidden()
        self.page.locator('#categoryNav [data-destination="agenda"]').click()
        expect(self.page).to_have_url(self.base+'#agenda')
        expect(self.page.locator('#agendaSection')).to_be_visible()
        expect(self.page.locator('#dashboardView')).to_be_hidden()
        expect(self.page.locator('#feedView')).to_be_hidden()
        self.page.reload()
        expect(self.page.locator('#agendaSection')).to_be_visible()
        expect(self.page.locator('#categoryNav [aria-current="page"]')).to_have_count(1)
        self.page.evaluate("goTo('all')")
        expect(self.page.locator('#feedView')).to_be_visible()
        expect(self.page.locator('#agendaSection')).to_be_hidden()

    def test_homepage_selection_has_one_lead_and_distinct_headlines(self):
        expect(self.page.locator('#dashboardFeature')).to_be_visible()
        expect(self.page.locator('#dashboardFeature > .article-card')).to_have_count(1)
        ids=self.page.locator('#dashboardFeature > [data-article-id],#dashboardRecent > [data-article-id]').evaluate_all('nodes=>nodes.map(n=>n.dataset.articleId)')
        self.assertGreaterEqual(len(ids),4)
        self.assertEqual(len(ids),len(set(ids)))
        expect(self.page.locator('#dashboardSavedPanel')).to_be_hidden()
        expect(self.page.locator('#dashboardView #coverageTools')).to_be_visible()
        self.page.evaluate("goTo('briefing')")
        expect(self.page.locator('#coverageTools')).to_be_hidden()

    def test_one_theme_and_legible_reference_palette(self):
        self.page.evaluate("setTheme('dark',true)")
        self.page.emulate_media(reduced_motion='reduce')
        colors=self.page.evaluate("() => ({bg:getComputedStyle(document.body).backgroundColor,text:getComputedStyle(document.body).color})")
        self.assertNotEqual(colors['bg'],colors['text'])
        sheets=self.page.locator('link[rel="stylesheet"]').evaluate_all('nodes=>nodes.map(n=>new URL(n.href).pathname.split("/").pop())')
        self.assertIn('dimension.css',sheets)
        self.assertFalse(set(sheets)&{'editorial.css','hashnode-preview.css','radar-hybrid.css','copper-theme.css','home-editorial.css','cosmic-theme.css','iaadc-editorial.css'})
        self.page.evaluate("setTheme('light',true)")
        self.assertNotEqual(self.page.evaluate('getComputedStyle(document.body).backgroundColor'),colors['bg'])

    def test_automatic_columns_use_available_space_and_preserve_a_saved_choice(self):
        self.page.evaluate("goTo('all')")
        expect(self.page.locator('#columnsCurrent')).to_have_text('Auto')
        self.assertGreaterEqual(self.page.locator('#articleGrid > .article-card').first.bounding_box()['width'],280)
        self.page.locator('#columnsToggle').click()
        self.page.locator('#columnsMenu [data-columns="2"]').click()
        self.page.reload()
        expect(self.page.locator('#columnsCurrent')).to_have_text('2')
        self.page.on('dialog',lambda dialog:dialog.accept())
        self.page.evaluate("document.getElementById('resetSettings').click()")
        expect(self.page.locator('#columnsCurrent')).to_have_text('Auto')
        for columns in ('5',None):
            preferences={'columns':columns} if columns else {}
            self.page.locator('#importData').set_input_files({'name':'preferences.json','mimeType':'application/json','buffer':json.dumps({'format':'radar-rss-settings-v3','preferences':preferences}).encode()})
            expect(self.page.locator('#columnsCurrent')).to_have_text(columns or 'Auto')
        self.page.reload()
        expect(self.page.locator('#columnsCurrent')).to_have_text('Auto')

    def test_closed_sidebar_keeps_news_visible_after_reload_and_mobile_resize(self):
        self.page.emulate_media(reduced_motion='reduce')
        self.page.evaluate("goTo('all')")
        self.page.locator('#menuToggle').click()
        expect(self.page.locator('#appSidebar')).to_be_hidden()
        for theme in ('light','dark'):
            self.page.evaluate('(theme)=>setTheme(theme,true)',theme)
            expect(self.page.locator('#articleGrid')).to_be_visible()
            self.assertGreaterEqual(self.page.locator('.page').bounding_box()['width'],1438)
            self.assertGreaterEqual(self.page.locator('#articleGrid > .article-card').first.bounding_box()['width'],280)
        self.page.reload()
        expect(self.page.locator('#appSidebar')).to_be_hidden()
        expect(self.page.locator('#articleGrid')).to_be_visible()
        self.assertGreaterEqual(self.page.locator('.page').bounding_box()['width'],1438)
        self.page.set_viewport_size({'width':320,'height':900})
        expect(self.page.locator('#articleGrid')).to_be_visible()
        self.assertGreaterEqual(self.page.locator('.page').bounding_box()['width'],318)
        self.page.locator('#menuToggle').click()
        expect(self.page.locator('#appSidebar')).to_be_visible()
        self.page.keyboard.press('Escape')
        expect(self.page.locator('#menuToggle')).to_be_focused()
        self.page.set_viewport_size({'width':1440,'height':1000})
        expect(self.page.locator('#appSidebar')).to_be_hidden()
        self.page.locator('#menuToggle').click()
        expect(self.page.locator('#appSidebar')).to_be_visible()
        self.assertGreaterEqual(self.page.locator('#articleGrid > .article-card').first.bounding_box()['width'],280)

    def test_forced_colors_has_an_unclipped_title_focus_indicator(self):
        self.page.evaluate("goTo('all')")
        self.page.emulate_media(reduced_motion='reduce',forced_colors='active')
        card=self.page.locator('#articleGrid > .article-card').first
        title=card.locator('.article-title a')
        self.page.keyboard.press('Tab')
        title.focus()
        expect(title).to_be_focused()
        # The inline link's own outline is clipped by its clamped heading;
        # the card must provide a visible alternative outside that clipping box.
        style=card.evaluate('n=>({style:getComputedStyle(n).outlineStyle,width:parseFloat(getComputedStyle(n).outlineWidth),offset:parseFloat(getComputedStyle(n).outlineOffset)})')
        self.assertNotEqual(style['style'],'none')
        self.assertGreaterEqual(style['width'],2)
        self.assertGreaterEqual(style['offset'],0)
        title.scroll_into_view_if_needed()
        output=Path('test-results/dimension');output.mkdir(parents=True,exist_ok=True)
        self.page.screenshot(path=str(output/'forced-title-focus.png'))

    def test_large_text_setting_reaches_home_agenda_summary_and_reader(self):
        document=deepcopy(fixtures.RESPONSES['events.json'])
        document['items']=[event('lectura',start=fixtures.STAMP[:10],timezone='UTC',title='Una actividad con nombre extenso para leer con comodidad')]
        self.page.route('**/data/events.json*',lambda route:route.fulfill(content_type='application/json',body=json.dumps(document)))
        self.page.reload()
        targets={'home':['#dashboardFeature .article-title','#dashboardRecent .dashboard-recent-title','#coveredList .covered-title'],
                 'all':['#articleGrid .article-title','#articleGrid .article-excerpt'],
                 'agenda':['.agenda-item-title','.agenda-meta'],
                 'briefing':['.briefing-title','.briefing-summary']}
        normal={}
        for width in (320,1440):
            self.page.set_viewport_size({'width':width,'height':900})
            for target,selectors in targets.items():
                self.page.evaluate('(target)=>goTo(target)',target)
                for selector in selectors:
                    node=self.page.locator(selector).first
                    expect(node).to_be_visible()
                    normal[width,selector]=node.evaluate('n=>parseFloat(getComputedStyle(n).fontSize)')
        self.page.locator('#settingsButton').click()
        self.page.locator('#settingFont').select_option('large')
        self.page.locator('#settingsDone').click()
        self.page.reload()
        self.assertEqual(self.page.evaluate('state.fontSize'),'large')
        for width in (320,1440):
            self.page.set_viewport_size({'width':width,'height':900})
            for target,selectors in targets.items():
                self.page.evaluate('(target)=>goTo(target)',target)
                for selector in selectors:
                    self.assertGreater(self.page.locator(selector).first.evaluate('n=>parseFloat(getComputedStyle(n).fontSize)'),normal[width,selector],selector)
                self.assertTrue(self.page.evaluate('document.documentElement.scrollWidth<=innerWidth+2'),(width,target))
            self.page.evaluate("goTo('all')")
            self.page.locator('#articleGrid .article-title a').first.click()
            expect(self.page.locator('#articleReaderDialog')).to_be_visible()
            self.assertGreaterEqual(self.page.locator('#readerSummary').evaluate('n=>parseFloat(getComputedStyle(n).fontSize)'),20)
            fixtures.check_visible_boxes(self.page,['#readerClose','#readerPrevious','#readerNext','#readerOpenOriginal'],f'large reader {width}')
            self.page.keyboard.press('Escape')

    def test_mobile_form_text_and_article_actions_are_easy_to_use(self):
        self.page.evaluate("goTo('all')")
        for width in (1440,390):
            self.page.set_viewport_size({'width':width,'height':900})
            actions=self.page.locator('#articleGrid > .article-card').first.locator('.article-read-toggle,.article-save,.article-more')
            for node in actions.all():
                box=node.bounding_box()
                self.assertGreaterEqual(min(box['width'],box['height']),44)
        self.page.locator('#searchToggle').click()
        self.assertGreaterEqual(self.page.locator('#searchInput').evaluate('n=>parseFloat(getComputedStyle(n).fontSize)'),16)
        self.page.locator('#settingsButton').click()
        for selector in ('#settingTheme','#settingFont'):
            self.assertGreaterEqual(self.page.locator(selector).evaluate('n=>parseFloat(getComputedStyle(n).fontSize)'),16)
        self.page.locator('#settingsDone').click()
        self.page.locator('#articleGrid .article-title a').first.click()
        expect(self.page.locator('#libraryTagInput')).to_be_visible()
        self.assertGreaterEqual(self.page.locator('#libraryTagInput').evaluate('n=>parseFloat(getComputedStyle(n).fontSize)'),16)

    def test_agenda_has_no_news_count_and_folder_counts_follow_their_sources(self):
        self.page.evaluate("markRead('noticia-0',true)")
        expect(self.page.locator('#categoryNav [data-destination="agenda"] .nav-count')).to_have_text('')
        for category in fixtures.CATEGORIES:
            expected=self.page.evaluate('(category)=>state.items.filter(x=>x.categories.includes(category)&&!state.read.has(x.id)).length',category)
            expect(self.page.locator('#libraryFolderNav .system-folder-link').filter(has=self.page.locator('.nav-label',has_text=category.split(' - ')[1])).locator('.nav-count')).to_have_text(str(expected))

    def test_direct_home_loads_coverage_and_topics_and_obeys_source_preferences(self):
        trends=deepcopy(fixtures.RESPONSES['trends.json'])
        trends['topics']=[{'label':'Tecnología','stories':4,'sources':2,'is_new':True}]
        self.page.route('**/data/trends.json*',lambda route:route.fulfill(content_type='application/json',body=json.dumps(trends)))
        self.page.goto(self.base+'#inicio')
        # Reload for a direct entry with no earlier route warming the trend cache.
        self.page.reload()
        expect(self.page.locator('#dashboardView #coverageTools')).to_be_visible()
        expect(self.page.locator('#coveredList > li').first).to_be_visible()
        expect(self.page.locator('#trendsPanel')).to_be_visible()
        title=self.page.locator('#coveredList .covered-title').first
        title.scroll_into_view_if_needed();title.focus()
        before=title.bounding_box()['y']
        title.press('Enter')
        expect(self.page.locator('#articleReaderDialog')).to_be_visible()
        self.page.keyboard.press('Escape')
        # The reader restores its logical origin in the next animation frame.
        self.page.evaluate('() => new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)))')
        expect(title).to_be_focused()
        self.assertLess(abs(title.bounding_box()['y']-before),3)
        # A pointer or assistive activation need not move DOM focus to a button.
        self.page.evaluate('document.activeElement.blur()')
        self.page.locator('#coveredList .covered-count').first.dispatch_event('click')
        expect(self.page.locator('#articleReaderDialog')).to_be_visible()
        self.page.keyboard.press('Escape')
        self.page.evaluate('() => new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)))')
        expect(title).to_be_focused()
        self.assertLess(abs(title.bounding_box()['y']-before),3)
        self.page.locator('#trendChips .trend-chip').first.click()
        expect(self.page.locator('#feedView')).to_be_visible()
        expect(self.page.locator('#searchInput')).to_have_value('Tecnología')
        self.page.evaluate("goTo('home')")
        self.page.evaluate('() => {state.sources.forEach(source=>state.hiddenSources.add(source.id));render()}')
        expect(self.page.locator('#coveredList .covered-item')).to_have_count(0)

    def test_no_news_shows_one_empty_state_without_an_empty_carousel(self):
        documents=deepcopy(fixtures.RESPONSES)
        documents['latest.json']['items']=[]
        documents['meta.json'].update(total_articles=0,latest_count=0)
        def route(request):
            name=request.request.url.split('/')[-1].split('?')[0]
            request.fulfill(content_type='application/json',body=json.dumps(documents.get(name,{})))
        self.page.route('**/data/**',route)
        self.page.reload()
        expect(self.page.locator('#dashboardFeature .dashboard-empty')).to_be_visible()
        expect(self.page.locator('.homepage-latest')).to_be_hidden()

    def test_selected_source_folder_and_icon_remain_legible_in_both_themes(self):
        self.page.emulate_media(reduced_motion='reduce')
        categories=[*fixtures.CATEGORIES,'08 - Monagas']
        self.page.evaluate('(categories)=>{state.categories=categories;buildNav()}',categories)
        failures=[]
        contrast=r"""node => {
          const rgba=c=>{const a=c.match(/[\d.]+/g).map(Number);return [a[0],a[1],a[2],a[3]??1]};
          const background=n=>{const c=rgba(getComputedStyle(n).backgroundColor);if(c[3]>=1||!n.parentElement)return c.slice(0,3);const below=background(n.parentElement);return c.slice(0,3).map((v,i)=>v*c[3]+below[i]*(1-c[3]));};
          const lum=rgb=>rgb.map(v=>{v/=255;return v<=.04045?v/12.92:((v+.055)/1.055)**2.4}).reduce((s,v,i)=>s+v*[.2126,.7152,.0722][i],0);
          return [node,...node.querySelectorAll('.nav-glyph,.nav-count')].filter(n=>n.getClientRects().length).map(n=>{const bg=lum(background(n)),fg=lum(rgba(getComputedStyle(n).color).slice(0,3));return (Math.max(fg,bg)+.05)/(Math.min(fg,bg)+.05)});
        }"""
        for category in categories:
            self.page.evaluate('(category)=>goTo(category)',category)
            expect(self.page.locator('#feedHeading')).to_have_text(category.split(' - ')[1])
            for theme in ('dark','light'):
                self.page.evaluate('(theme)=>setTheme(theme,true)',theme)
                ratios=self.page.locator('#libraryFolderNav .nav-link.active').evaluate(contrast)
                if min(ratios)<4.5:failures.append((category,theme,ratios))
        self.page.evaluate("goTo('all')")
        expect(self.page.locator('#feedHeading')).to_have_text('Todas las noticias')
        for theme in ('dark','light'):
            self.page.evaluate('(theme)=>setTheme(theme,true)',theme)
            ratios=self.page.locator('#categoryNav [data-destination="all"]').evaluate(contrast)
            if min(ratios)<4.5:failures.append(('Noticias',theme,ratios))
        self.assertFalse(failures,failures)

    def test_category_symbols_are_distinct_and_custom_folders_have_a_symbol(self):
        expect(self.page.locator('#dashboardTitle')).to_have_text('Actualidad')
        self.assertTrue(self.page.locator('.brand-mark img').evaluate('n=>n.complete&&n.naturalWidth>0'))
        brand=self.page.locator('.brand-mark img').bounding_box()
        self.assertEqual((brand['width'],brand['height']),(24,24))
        categories=[*fixtures.CATEGORIES,'08 - Monagas']
        self.page.evaluate('(categories)=>{state.categories=categories;buildNav()}',categories)
        symbols=self.page.locator('#libraryFolderNav .system-folder-link .nav-glyph svg').evaluate_all('nodes=>nodes.map(n=>n.innerHTML)')
        self.assertEqual(len(set(symbols)),8,'Each category needs its own recognizable symbol')
        folder=self.page.evaluate("svgIcon('folder').innerHTML")
        fallback=self.page.evaluate("svgIcon('unknown').innerHTML")
        self.assertNotEqual(folder,fallback,'Manual folders must not fall back to a newspaper')

    def test_cards_have_depth_and_focus_feedback_without_breaking_the_reader(self):
        self.page.emulate_media(reduced_motion='reduce')
        self.page.evaluate("goTo('all')")
        card=self.page.locator('#articleGrid > .article-card').first
        idle=card.evaluate('n=>({shadow:getComputedStyle(n).boxShadow,border:getComputedStyle(n).borderTopColor})')
        self.assertNotEqual(idle['shadow'],'none','Cards need visible depth at rest')
        title=card.locator('.article-title a');title.focus()
        focused=card.evaluate('n=>({shadow:getComputedStyle(n).boxShadow,border:getComputedStyle(n).borderTopColor})')
        self.assertNotEqual(focused,idle,'Focusing a card must highlight its edge')
        title.press('Enter')
        expect(self.page.locator('#articleReaderDialog')).to_be_visible()
        self.page.keyboard.press('Escape')
        expect(title).to_be_focused()
        self.page.emulate_media(reduced_motion='reduce',forced_colors='active')
        self.assertNotEqual(title.evaluate('n=>getComputedStyle(n).outlineStyle'),'none')
        self.page.emulate_media(reduced_motion='reduce',forced_colors='none')
        active=card.evaluate('n=>[getComputedStyle(n).animationName,getComputedStyle(n).transitionDuration]')
        self.assertEqual(active,['none','0s'])

    def test_mobile_menu_and_routes_do_not_overflow(self):
        for width in (320,390,768,1440):
            with self.subTest(width=width):
                self.page.set_viewport_size({'width':width,'height':900})
                for target in ('home','all','agenda','briefing'):
                    self.page.evaluate('(target)=>goTo(target)',target)
                    self.page.wait_for_function('(target)=>state.pageView===target',arg={'home':'dashboard','all':'feed','agenda':'agenda','briefing':'briefing'}[target])
                    self.assertTrue(self.page.evaluate('document.documentElement.scrollWidth<=innerWidth+2'))
                if width<=950:
                    self.page.locator('#menuToggle').click()
                    expect(self.page.locator('#appSidebar')).to_have_attribute('aria-modal','true')
                    self.page.keyboard.press('Escape')
                    expect(self.page.locator('#menuToggle')).to_be_focused()
        output=Path('test-results/dimension');output.mkdir(parents=True,exist_ok=True)
        for width in (390,1440):
            self.page.set_viewport_size({'width':width,'height':1000})
            for theme in ('dark','light'):
                self.page.evaluate('(theme)=>setTheme(theme,true)',theme)
                self.page.evaluate("goTo('home')")
                expect(self.page.locator('#dashboardView')).to_be_visible()
                self.page.screenshot(path=str(output/f'{theme}-{width}.png'),full_page=True,animations='disabled')


if __name__=='__main__':unittest.main(verbosity=2)
