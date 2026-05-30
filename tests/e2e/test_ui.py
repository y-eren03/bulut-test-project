import pytest
from playwright.sync_api import Page, expect
import os

# Uygulamanın çalıştığı varsayılan URL
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

# Arka planda uvicorn sunucusunu başlatmak için live_server fixture'ını kullan
pytestmark = pytest.mark.usefixtures("live_server")

def test_homepage_loads(page: Page):
    """Ana sayfanın doğru şekilde yüklendiğini kontrol eder."""
    page.goto(BASE_URL)
    
    # Başlığın To-Do List Manager içerdiğini kontrol et
    expect(page).to_have_title("To-Do List Manager")
    
    # H1 etiketinin varlığını kontrol et
    expect(page.locator("h1")).to_contain_text("To-Do List Manager")

def test_add_task(page: Page):
    """Yeni bir görev eklenebildiğini kontrol eder."""
    page.goto(BASE_URL)
    
    # Input alanlarını doldur
    page.fill("#taskTitle", "E2E Test Task")
    page.fill("#taskDesc", "Playwright E2E testing")
    
    # Ekle butonuna tıkla
    page.click("button:has-text('Ekle')")
    
    # Görevin listeye eklendiğini doğrula
    # API çağrısı ve DOM güncellemesi için kısa bir süre bekleyebiliriz
    expect(page.locator("#taskList")).to_contain_text("E2E Test Task")
    
def test_complete_task(page: Page):
    """Bir görevin tamamlanabildiğini test eder."""
    page.goto(BASE_URL)
    
    # Önce bir görev ekleyelim (eğer liste boşsa diye)
    page.fill("#taskTitle", "Complete Me")
    page.click("button:has-text('Ekle')")
    
    # Sadece yeni eklediğimiz "Complete Me" görevinin yanındaki "Tamamla" butonuna tıkla
    task_item = page.locator(".task", has_text="Complete Me").last
    task_item.locator("button:has-text('Tamamla')").click()
    
    # Görevin css class'ının .completed içerdiğini kontrol et
    import re
    expect(task_item).to_have_class(re.compile("completed"))
