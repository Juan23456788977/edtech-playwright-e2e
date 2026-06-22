import time
from playwright.sync_api import sync_playwright

def run():
    p = sync_playwright().start()
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(viewport={'width': 1366, 'height': 900})
    page = context.new_page()

    BASE_URL = 'https://edge.akdemia.com'
    page.goto(f'{BASE_URL}/login')
    page.fill('#email_login', 'jcortez@akdemia.com')
    page.fill('#password_login', 'akdemia#2026*')
    page.click('input[type="submit"]')
    page.wait_for_load_state('networkidle')
    
    # Click change role
    page.evaluate('''() => {
        let el = document.querySelector('a[href="#change-role-modal"]');
        if(el) el.click();
    }''')
    time.sleep(1)
    
    # Type and wait for ajax
    page.fill('#fill-school', 'Colegio Demo Satisfacción')
    
    # Wait for the item to appear in the ul
    try:
        page.wait_for_selector('ul#change-role li', timeout=5000)
    except:
        pass
    time.sleep(2) # Extra time just in case
    
    # Click the matching item
    page.evaluate('''() => {
        let items = Array.from(document.querySelectorAll('ul#change-role li a'));
        let target = items.find(a => a.innerText.includes('Colegio Demo Satisfacción'));
        if (target) target.click();
    }''')
    time.sleep(1)
    
    # Click Cambiar
    page.evaluate('''() => {
        let btn = document.querySelector('#change-role-button');
        if(btn) btn.click();
    }''')
    page.wait_for_load_state('networkidle')
    time.sleep(3)
    
    print("URL after changing school:", page.url)
    
    # Go to Reportes
    page.goto(f'{BASE_URL}/reports/group')
    page.wait_for_load_state('networkidle')
    time.sleep(3)
    
    # Extract Ministry reports
    reports = page.evaluate('''() => {
        let result = [];
        // The table has <th>Ministerio</th> as the second th.
        let rows = document.querySelectorAll('tbody.with-inline tr');
        rows.forEach(row => {
            let cells = row.querySelectorAll('td');
            if (cells.length > 1) {
                let p = cells[1].querySelector('p');
                if (p && p.innerText.trim() !== '') {
                    result.push({
                        name: p.innerText.trim(),
                        title: p.getAttribute('title') || ''
                    });
                }
            }
        });
        return result;
    }''')
    
    print("MINISTRY REPORTS:")
    # deduplicate
    seen = set()
    for r in reports:
        item = f"- {r['name']}: {r['title']}"
        if item not in seen:
            print(item)
            seen.add(item)
            
    context.close()
    browser.close()
    p.stop()

if __name__ == '__main__':
    run()
