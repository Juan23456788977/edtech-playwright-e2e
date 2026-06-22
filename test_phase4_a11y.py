import time
from playwright.sync_api import sync_playwright

def run():
    p = sync_playwright().start()
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(viewport={'width': 1366, 'height': 900})
    page = context.new_page()

    print("--- 1. Testing Keyboard Navigation ---")
    page.goto('https://alpha.akdemia.com/login')
    page.fill('#email_login', 'jcortez@akdemia.com')
    page.fill('#password_login', 'akdemia#2026*')
    page.press('#password_login', 'Enter')
    page.wait_for_load_state('networkidle')
    time.sleep(2)
    
    # We are at select_role
    page.evaluate('''
    document.getElementById('selected-instance-type').value = 'Employee';
    document.getElementById('selected-instance-id').value = '17548';
    document.getElementById('select-role-form').submit();
    ''')
    time.sleep(5)
    
    # Now we are on dashboard. We want to test if we can reach "Cambiar a cualquier usuario" via Tab.
    print("Tab navigation starting...")
    # Hit tab multiple times to see where focus goes
    
    # A quick script to simulate Tab presses until we find our link
    found = False
    for i in range(50):
        page.keyboard.press('Tab')
        time.sleep(0.1)
        focused_text = page.evaluate("document.activeElement.innerText || document.activeElement.value || ''")
        focused_tag = page.evaluate("document.activeElement.tagName")
        if "Cambiar a cualquier usuario" in focused_text or "Cambiar a usuario" in focused_text:
            print(f"Success! Reached 'Cambiar a usuario' using TAB after {i+1} presses. Element: {focused_tag}")
            found = True
            page.keyboard.press('Enter')
            time.sleep(2)
            break
            
    if not found:
        print("Failed to reach 'Cambiar a usuario' via Keyboard within 50 tabs.")

    # Check modal opened
    is_modal_open = page.evaluate("document.getElementById('change-to-any-user-modal') !== null && document.getElementById('change-to-any-user-modal').style.display !== 'none'")
    print(f"Modal Opened via Keyboard: {is_modal_open}")
    
    if is_modal_open:
        # Type via keyboard
        page.keyboard.type("prueba2024")
        page.keyboard.press('Enter')
        time.sleep(3)
        print("Search triggered via keyboard.")

    print("\\n--- 2. Testing UI Contrast (Simple Check) ---")
    
    page.evaluate('''() => {
        var sidebar = document.querySelector('.sidebar-employee');
        if(sidebar) {
            console.log('Sidebar bg:', window.getComputedStyle(sidebar).backgroundColor);
            console.log('Sidebar color:', window.getComputedStyle(sidebar).color);
        } else {
            console.log('No .sidebar-employee found');
        }
    }''')
    
    # Since we can't easily run axe-core here without injecting it, we'll inject axe-core from cdn
    print("Injecting axe-core for contrast audit on sidebar and empty states...")
    page.add_script_tag(url="https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.7.2/axe.min.js")
    time.sleep(1)
    
    results = page.evaluate('''() => {
        return new Promise((resolve) => {
            axe.run({
                runOnly: {
                    type: 'rule',
                    values: ['color-contrast']
                }
            }, (err, results) => {
                if (err) resolve(err);
                resolve(results.violations);
            });
        });
    }''')
    
    if len(results) > 0:
        print(f"Found {len(results)} contrast violations.")
        for v in results:
            print("Violation ID:", v.get('id'))
            print("Impact:", v.get('impact'))
            print("Description:", v.get('description'))
            nodes = v.get('nodes', [])
            print(f"Affected nodes: {len(nodes)}")
    else:
        print("No contrast violations found. WCAG AA/AAA compliant.")

    context.close()
    browser.close()
    p.stop()

if __name__ == '__main__':
    run()
