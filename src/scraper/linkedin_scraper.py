# src/scraper/linkedin_scraper.py

import os
import time
import json
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from selenium.webdriver.remote.webelement import WebElement

class LinkedInScraper:
    def __init__(self, headless=False):
        firefox_options = FirefoxOptions()
        if headless:
            firefox_options.add_argument("--headless")
        firefox_options.add_argument("--width=1920")
        firefox_options.add_argument("--height=1080")
        firefox_options.set_preference("general.useragent.override", 
                                      "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0")
        
        self.driver = webdriver.Firefox(
            service=FirefoxService(executable_path="/snap/bin/geckodriver"),
            options=firefox_options
        )
        self.wait = WebDriverWait(self.driver, 20)
    
    def login_manual(self):
        """Login manual al usuario para evitar bloqueos de seguridad."""
        print("Iniciando sesión en LinkedIn...")
        print("1. Se abrirá LinkedIn. Inicia sesión manualmente.")
        print("2. Completa el inicio de sesión y resuelve cualquier desafío de seguridad.")
        print("3. Regresa a esta terminal y presiona Enter para continuar.")
        
        self.driver.get("https://www.linkedin.com/login")
        
        # Esperar a que el usuario complete el login
        input("Presiona Enter después de iniciar sesión en LinkedIn...")
        
        # Verificar que el login fue exitoso navegando a la página principal
        try:
            self.driver.get("https://www.linkedin.com/feed/")
            time.sleep(3)
            if "feed" in self.driver.current_url or "linkedin" in self.driver.current_url:
                print("Login exitoso!")
                return True
        except Exception as e:
            print(f"No se pudo verificar el login: {e}. Continuando de todos modos...")
        
        return True
    
    def _scroll_to_bottom(self):
        """Hace scroll hasta el fondo de la página para cargar contenido dinámico."""
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        for _ in range(5):
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
    
    def extract_profile(self, profile_url):
        """Extrae información completa del perfil de LinkedIn con múltiples estrategias."""
        clean_url = profile_url.split("?")[0]  # Remover parámetros innecesarios
        if not clean_url.startswith("https://www.linkedin.com/in/"):
            clean_url = f"https://www.linkedin.com/in/{clean_url.split('/')[-2]}"
        
        print(f"Extrayendo perfil: {clean_url}")
        self.driver.get(clean_url)
        time.sleep(5)  # Dar tiempo a carga completa
        self._scroll_to_bottom()
        
        profile_data = {
            "name": "",
            "headline": "",
            "location": "",
            "summary": "",
            "experience": [],
            "education": [],
            "skills": [],
            "contact_info": {},
            "profile_image": ""
        }
        
        # Extraer nombre - múltiples estrategias
        profile_data["name"] = self._extract_name()
        
        # Extraer headline - múltiples estrategias
        profile_data["headline"] = self._extract_headline()
        
        # Extraer ubicación
        profile_data["location"] = self._extract_location_info()
        
        # Extraer resumen
        profile_data["summary"] = self._extract_summary()
        
        # Extraer habilidades
        profile_data["skills"] = self._extract_skills()
        
        # Extraer experiencia
        profile_data["experience"] = self._extract_experience_from_profile()
        
        # Extraer educación
        profile_data["education"] = self._extract_education()
        
        print(f"Perfil extraído: {profile_data['name']}")
        return profile_data
    
    def _extract_name(self):
        """Extrae el nombre usando múltiples estrategias."""
        strategies = [
            # Estrategia 1: Selector CSS moderno
            lambda: self._find_element_text(By.CSS_SELECTOR, "h1.text-heading-xlarge:not(.visually-hidden)"),
            # Estrategia 2: XPath para primer h1
            lambda: self._find_element_text(By.XPATH, "//h1[not(contains(@class, 'visually-hidden'))][1]"),
            # Estrategia 3: Elemento con data-control-name
            lambda: self._find_element_text(By.CSS_SELECTOR, "[data-control-name='top_card_name']"),
            # Estrategia 4: Primer h1 con suficiente texto
            lambda: self._find_long_text_h1(),
        ]
        
        for strategy in strategies:
            try:
                name = strategy()
                if name and len(name.strip()) > 2:
                    return name.strip()
            except Exception:
                continue
        return ""
    
    def _extract_headline(self):
        """Extrae el headline usando múltiples estrategias."""
        strategies = [
            # Estrategia 1: Div segundo con texto (headline suele ser segundo elemento destacado)
            lambda: self._find_element_text(By.XPATH, "//div[contains(@class, 'text-body-medium') and not(contains(@class, 'visually-hidden'))]"),
            # Estrategia 2: XPath alternativo
            lambda: self._find_element_text(By.XPATH, "//h2[contains(text(), 'About')]/preceding::div[contains(@class, 'display-flex')][1]"),
            # Estrategia 3: Buscar texto después del nombre
            lambda: self._find_headline_after_name(),
        ]
        
        for strategy in strategies:
            try:
                headline = strategy()
                if headline and len(headline.strip()) > 5:
                    return headline.strip()
            except Exception:
                continue
        return ""
    
    def _extract_summary(self):
        """Extrae la sección de resumen/about."""
        try:
            # Estrategia 1: Sección About con XPath
            summary_section = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//h2[contains(text(), 'About')]/ancestor::section/following-sibling::section"))
            )
            return summary_section.text.strip()
        except (TimeoutException, NoSuchElementException):
            try:
                # Estrategia 2: Buscar el primer texto significativo después de About
                about_header = self.driver.find_element(By.XPATH, "//h2[contains(text(), 'About')]")
                parent = about_header.find_element(By.XPATH, "./ancestor::section")
                next_section = parent.find_element(By.XPATH, "./following-sibling::section[1]")
                return next_section.text.strip()
            except:
                pass
        
        return ""
    
    def _extract_skills(self):
        """Extrae la lista de habilidades navegando a la sección correspondiente."""
        skills = []
        
        # Primero extraer habilidades visibles en el perfil principal
        try:
            skill_elements = self.driver.find_elements(By.CSS_SELECTOR, ".skill-category-entity__name, [data-view-name='skill'] span")
            for elem in skill_elements[:15]:
                text = elem.text.strip()
                if text and len(text) < 50:
                    skills.append(text)
        except:
            pass
        
        # Si no hay habilidades visibles, navegar a detalles/skills
        if not skills:
            try:
                current_url = self.driver.current_url
                skills_url = f"{current_url.split('?')[0]}details/skills/"
                self.driver.get(skills_url)
                time.sleep(3)
                
                # Extraer habilidades mostradas en la página de habilidades
                skill_elements = self.wait.until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "span[aria-hidden='true']"))
                )
                
                for elem in skill_elements:
                    text = elem.text.strip()
                    if text and len(text) < 50 and not any(char.isdigit() for char in text):
                        skills.append(text)
                        
            except Exception as e:
                print(f"Error extrayendo habilidades: {e}")
        
        # Deduplicar y limitar
        seen = set()
        unique_skills = []
        for skill in skills:
            if skill.lower() not in seen:
                seen.add(skill.lower())
                unique_skills.append(skill)
        
        return unique_skills[:20]
    
    def _extract_experience_from_profile(self):
        """Extrae experiencia laboral desde el perfil principal."""
        experience = []
        
        try:
            # Navegar a la sección de experiencia
            experience_url = f"{self.driver.current_url.split('?')[0]}details/experience/"
            self.driver.get(experience_url)
            time.sleep(5)
            
            # Estrategia 1: Buscar elementos con estructura de empleo
            job_containers = self.driver.find_elements(By.CSS_SELECTOR, 
                "li[data-view-name='position'], div[data-view-name='positionDetails'], li[class*='job']")
            
            # Estrategia 2: Buscar secciones que contengan 'Experience'
            if not job_containers:
                experience_sections = self.driver.find_elements(By.XPATH, 
                    "//section[contains(@class, 'section') and contains(., 'Experience')]")
                if experience_sections:
                    job_containers = experience_sections[0].find_elements(By.TAG_NAME, "li")
            
            # Estrategia 3: Buscar listas con información de empleo
            if not job_containers:
                all_lists = self.driver.find_elements(By.TAG_NAME, "ul")
                for ul in all_lists:
                    if "Experience" in ul.text or "Employment" in ul.text:
                        job_containers = ul.find_elements(By.TAG_NAME, "li")
                        break
            
            # Procesar cada contenedor
            for i, container in enumerate(job_containers[:5]):
                try:
                    # Extraer título
                    title = ""
                    try:
                        title_elem = container.find_element(By.CSS_SELECTOR, "h3")
                        title = title_elem.text.strip()
                    except:
                        # Intentar con XPath
                        try:
                            title_elem = container.find_element(By.XPATH, ".//h3")
                            title = title_elem.text.strip()
                        except:
                            pass
                    
                    # Extraer empresa
                    company = ""
                    try:
                        company_elem = container.find_element(By.CSS_SELECTOR, "h4")
                        company = company_elem.text.strip()
                    except:
                        try:
                            company_elem = container.find_element(By.XPATH, ".//h4")
                            company = company_elem.text.strip()
                        except:
                            pass
                    
                    # Extraer fechas
                    dates = ""
                    try:
                        date_elem = container.find_element(By.CSS_SELECTOR, ".date-range, .date, span[class*='date']")
                        dates = date_elem.text.strip()
                    except:
                        # Intentar extraer de texto completo
                        full_text = container.text
                        date_match = re.search(r'([A-Z][a-z]+ \d{4}.*?)(\n|$)', full_text)
                        if date_match:
                            dates = date_match.group(1)
                    
                    if title or company:
                        experience.append({
                            "title": title,
                            "company": company,
                            "dates": dates,
                            "location": "",
                            "description": ""
                        })
                except Exception as e:
                    print(f"Error en empleo #{i}: {e}")
                    continue
        
        except Exception as e:
            print(f"Error navegando a experiencia: {e}")
            # Fallback: extraer desde perfil principal
            experience = self._extract_experience_fallback()
        
        return experience
    
    def _extract_experience_fallback(self):
        """Extracción de experiencia alternativa desde perfil principal."""
        # Regresar al perfil principal
        self.driver.back()
        time.sleep(3)
        
        experience = []
        try:
            # Buscar elementos que contengan información de empleo
            job_elements = self.driver.find_elements(By.XPATH, 
                "//li[contains(@class, 'job') or contains(@class, 'experience') or contains(., 'Present') or contains(., '202')]")
            
            # Alternativa: buscar por texto destacado
            if not job_elements:
                job_elements = self.driver.find_elements(By.XPATH, 
                    "//div[contains(@class, 'display-flex') and contains(., 'Present') or contains(., '2020') or contains(., '2021')]")
            
            for elem in job_elements[:5]:
                try:
                    text = elem.text
                    lines = [line.strip() for line in text.split('\n') if line.strip()]
                    
                    if len(lines) >= 2:
                        experience.append({
                            "title": lines[0],
                            "company": lines[1] if len(lines) > 1 else "",
                            "dates": lines[2] if len(lines) > 2 else "",
                            "location": "",
                            "description": ""
                        })
                except:
                    continue
        except Exception as e:
            print(f"Error en extracción alternativa: {e}")
        
        return experience
    
    def _extract_education(self):
        """Extrae información educativa."""
        education = []
        try:
            ed_url = f"{self.driver.current_url.split('?')[0]}details/education/"
            self.driver.get(ed_url)
            time.sleep(3)
            
            edu_items = self.driver.find_elements(By.CSS_SELECTOR, "li")
            for item in edu_items[:5]:
                try:
                    text_parts = item.text.split('\n')
                    if len(text_parts) >= 2 and any(word in text_parts[0].lower() for word in ['university', 'college', 'institute', 'degree']):
                        education.append({
                            "institution": text_parts[0],
                            "degree": text_parts[1] if len(text_parts) > 1 else "",
                            "dates": text_parts[2] if len(text_parts) > 2 else ""
                        })
                except:
                    continue
        except Exception as e:
            print(f"Error extrayendo educación: {e}")
        
        return education
    
    def _extract_location_info(self):
        """Extrae información de ubicación."""
        try:
            # Buscar texto que parezca ubicación (después del headline)
            elements = self.driver.find_elements(By.CSS_SELECTOR, "div.text-body-small, span.text-body-small")
            for elem in elements:
                text = elem.text.strip()
                if text and "," in text and len(text) < 100:  # Formato típico: "Ciudad, País"
                    return text
        except:
            pass
        return ""
    
    def _find_element_text(self, by, locator):
        """Busca y retorna el texto de un elemento, si existe."""
        try:
            element = self.wait.until(
                EC.presence_of_element_located((by, locator))
            )
            return element.text
        except:
            return ""
    
    def _find_long_text_h1(self):
        """Encuentra el primer h1 que tenga suficiente texto (probablemente nombre)."""
        try:
            h1_elements = self.driver.find_elements(By.TAG_NAME, "h1")
            for elem in h1_elements:
                text = elem.text.strip()
                if len(text) > 2 and len(text) < 100:  # Nombres típicamente cortos
                    return text
            return ""
        except:
            return ""
    
    def _find_headline_after_name(self):
        """Busca el headline como texto después del nombre."""
        try:
            h1_elements = self.driver.find_elements(By.TAG_NAME, "h1")
            for elem in h1_elements:
                # Buscar texto significativo cerca del nombre
                parent = elem.find_element(By.XPATH, "./ancestor::section")
                sibling_texts = parent.find_elements(By.XPATH, ".//div[contains(@class, 'display-flex')]")
                for i, sibling in enumerate(sibling_texts):
                    text = sibling.text.strip()
                    if text and i > 0 and len(text) > 20:  # Evitar el nombre
                        return text
            return ""
        except:
            return ""
    
    def save_profile(self, profile_data, filename="profile_data.json"):
        """Guarda los datos extraídos en un archivo JSON."""
        output_path = os.path.join(os.path.dirname(__file__), "..", "..", "assets", filename)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(profile_data, f, indent=2, ensure_ascii=False)
        print(f"Datos guardados en: {output_path}")
    
    def close(self):
        """Cierra el navegador."""
        self.driver.quit()

# Proof-of-concept principal
if __name__ == "__main__":
    scraper = LinkedInScraper(headless=False)
    
    try:
        # Paso 1: Login manual
        scraper.login_manual()
        
        # Paso 2: Extraer perfil (usar tu URL de LinkedIn)
        profile_url = "https://www.linkedin.com/in/gerardobenitez/"
        profile_data = scraper.extract_profile(profile_url)
        
        # Paso 3: Guardar resultados
        scraper.save_profile(profile_data)
        
        print("\n=== RESULTADOS DEL SCRAPING ===")
        print(json.dumps(profile_data, indent=2, ensure_ascii=False))
        
    finally:
        scraper.close()