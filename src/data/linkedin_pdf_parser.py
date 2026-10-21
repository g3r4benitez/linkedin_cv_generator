"""Parser para extraer y estructurar datos del PDF de LinkedIn."""
import re
import json
import os
from typing import Dict, List, Any
import pdfplumber

class LinkedInPDFParser:
    """Parsea el PDF exportado de LinkedIn y estructura los datos."""

    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.raw_text = ""
        self.data = {}

    def extract_text(self) -> str:
        """Extrae todo el texto del PDF."""
        with pdfplumber.open(self.pdf_path) as pdf:
            full_text = ""
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    full_text += text + "\n"
            self.raw_text = full_text
        return self.raw_text

    def parse(self) -> Dict[str, Any]:
        """Parsea el texto y devuelve estructura de datos."""
        text = self.extract_text()
        lines = text.split('\n')

        data = {
            "name": "",
            "contact_info": {},
            "headline": "",
            "summary": "",
            "skills": [],
            "experience": [],
            "education": [],
            "languages": []
        }

        # Extraer nombre, headline y contacto (primeras líneas)
        self._parse_contact_section(lines, data)

        # Extraer habilidades
        data["skills"] = self._parse_skills_section(lines)

        # Extraer experiencia
        data["experience"] = self._parse_experience_section(lines)

        # Extraer educación
        data["education"] = self._parse_education_section(lines)

        # Extraer idiomas
        data["languages"] = self._parse_languages(lines)

        # Extraer resumen
        data["summary"] = self._parse_summary_section(lines)

        self.data = data
        return data

    def _parse_contact_section(self, lines: List[str], data: Dict):
        """Extrae nombre, headline y contacto."""
        # Buscar la línea que contiene "Contact"
        contact_line_idx = -1
        for i, line in enumerate(lines):
            if "Contact " in line or line.strip() == "Contact":
                contact_line_idx = i
                break

        if contact_line_idx == -1:
            return

        # Nombre
        name_match = re.search(r"Contact\s+([A-Z][a-z]+ [A-Z][a-z]+)", lines[contact_line_idx])
        if name_match:
            data["name"] = name_match.group(1)

        # Headline
        headline_parts = []

        for i in range(contact_line_idx + 1, min(contact_line_idx + 10, len(lines))):
            line = lines[i].strip()

            if not line:
                continue

            # Ignorar líneas de ubicación
            if line.startswith("Provincia") or line == "Argentina," or \
               ("Buenos Aires" in line and len(line) < 50):
                continue

            # Ignorar email y links
            if "@" in line or "www." in line or "linkedin.com" in line:
                break

            # Procesar línea con número de teléfono
            if re.search(r"\+\d{10,}", line):
                after_phone = re.split(r"\+\d{10,}\s*\(Mobile\)\s*", line)
                if len(after_phone) > 1:
                    headline_parts.append(after_phone[1].strip())
                continue

            # Procesar línea de headline (empieza con "|" o contiene "|")
            if "|" in line:
                if line.startswith("Argentina"):
                    line = line.replace("Argentina", "").strip()
                headline_parts.append(line)

        # Unir y limpiar el headline
        if headline_parts:
            full_headline = " | ".join(headline_parts).strip(" |")
            tech_items = []
            for item in full_headline.split("|"):
                item = item.strip()
                if item and item not in tech_items:
                    tech_items.append(item)
            data["headline"] = " | ".join(tech_items)

        # Información de contacto
        joined_text = '\n'.join(lines[contact_line_idx:contact_line_idx + 10])
        phone_match = re.search(r"\+(\d{10,})", joined_text)
        email_match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", joined_text)

        data["contact_info"] = {
            "phone": phone_match.group(0) if phone_match else "",
            "email": email_match.group(0) if email_match else ""
        }

    def _parse_skills_section(self, lines: List[str]) -> List[str]:
        """Extrae la lista de habilidades técnicas."""
        skills = []
        top_skills_section = []

        tech_keywords = [
            "python", "fastapi", "docker", "aws", "react", 
            "javascript", "typescript", "nodejs", "postgres", "postgresql",
            "kafka", "rabbitmq", "celery", "django", "flask", "nestjs",
            "tornado", "php", "mysql", "jquery", "symfony",
            "laravel", "vue", "angular", "graphql",
            "redis", "mongo", "kubernetes", "terraform", "linux",
            "git", "ci/cd", "jenkins", "gitlab", "lambda", "apigateway",
            "sqs", "sns", "rest", "api", "microservices",
            "pytest", "unit", "testing", "agile", "scrum", "sass",
            "langchain", "rag", "ai", "machine", "ml", "gcp", "azure",
            "asp", "flash", "actionscript", "serverless", "athena",
            "nestjs", "nestjs", "nestjs", "nodejs",
            # Keywords adicionales
            "html", "css", "sass", "saas", "nextjs", "express", "sequelize",
            "typeorm", "prisma", "supabase", "firebase", "auth0", "okta",
        ]

        # 1. PARSEAR SECCIÓN "Top Skills" PRIMERO (prioridad máxima)
        in_skills_section = False
        for i, line in enumerate(lines):
            if "Top Skills" in line:
                in_skills_section = True
                continue

            if in_skills_section:
                stripped = line.strip()

                # Terminar al encontrar la siguiente sección
                # Considerar errores de OCR como "Experietnce" o "Languajes"
                lower_line = stripped.lower()
                if (lower_line.startswith("experience") or 
                    stripped.startswith("Experi") or  # catches "Experietnce"
                    lower_line.startswith("education") or
                    lower_line.startswith("languag") or  # catches "Languages", "Languajes"
                    lower_line.startswith("skill") or    # catches "Skills" (not "Top Skills")
                    lower_line.startswith("summary") or
                    stripped == "Page" or
                    stripped.startswith("Page ")):
                    break

                # Extraer habilidades: líneas cortas y técnicas
                if stripped and len(stripped) < 40 and len(stripped) > 1:
                    # Filtrar texto descriptivo no técnico
                    desc_filter = [
                        "architectures", "principles", "operations", "requirements",
                        "development", "systems", "design", "testing", "documentation",
                        "layers", "integration", "processes", "solutions", "communication",
                        "serverless", "queues", "teams", "delivery",
                        "efficiency", "engagement", "accessibility", "information",
                        "handling", "deployment", "capability", "architecture",
                        "years", "worked", "knowledge", "managed", "implemented",
                        "created", "developed", "sources", "forward", "platform",
                    ]

                    if not any(word in lower_line for word in desc_filter):
                        # Verificar que sea algo técnico
                        if any(tech.lower() in lower_line for tech in tech_keywords):
                            top_skills_section.append(stripped)

        # Agregar las habilidades de la sección "Top Skills" con prioridad
        for skill in top_skills_section:
            normalized = skill.strip()
            if normalized and normalized.lower() not in [s.lower() for s in skills]:
                skills.append(normalized)

        # 2. Extraer habilidades del headline (si existe)
        if self.data.get("headline"):
            headline_skills = [s.strip() for s in self.data["headline"].split("|") if s.strip()]
            for skill in headline_skills:
                # Extraer solo el nombre técnico (eliminar prefijos no técnicos)
                for part in skill.split():
                    part_clean = part.strip()
                    if part_clean and part_clean.lower() in [t.lower() for t in tech_keywords]:
                        if part_clean not in skills and part_clean.lower() not in [s.lower() for s in skills]:
                            skills.append(part_clean)
                # También agregar habilidades completas del headline
                for tech in tech_keywords:
                    if tech.lower() in skill.lower() and skill not in skills and skill.lower() not in [s.lower() for s in skills]:
                        skills.append(skill)

        # 3. Buscar patrones técnicos en el texto completo (complemento)
        full_text = '\n'.join(lines)
        tech_patterns = [
            r"RabbitMQ", r"Celery", r"Kafka", r"Apache Airflow", r"Tornado",
            r"MySQL", r"jQuery", r"ASP\.NET", r"Flash", r"ActionScript",
            r"Serverless", r"Athena", r"Bitrix24", r"Paypal", r"Twilio",
            r"Google APIs", r"AWS", r"GCP", r"Azure", r"Docker",
            r"Kubernetes", r"Terraform", r"Git", r"CI/CD", r"Jenkins",
            r"GitLab", r"Lambda", r"API Gateway", r"PostgreSQL", r"Redis",
            r"MongoDB", r"Vue\.js", r"Angular", r"Symfony", r"Laravel",
            r"TypeScript", r"GraphQL", r"Pytest", r"Selenium", r"Jest",
            r"React\.js", r"Node\.js", r"NestJS", r"FastAPI", r"Django",
            r"Flask", r"Rest API", r"Microservices", r"Python", r"Javascript",
            r"Langchain", r"Redis", r"RabbitMQ"
        ]

        for pattern in tech_patterns:
            matches = re.findall(pattern, full_text, re.IGNORECASE)
            for match in matches:
                normalized = match.strip()
                if normalized and normalized.lower() not in [s.lower() for s in skills]:
                    skills.append(normalized)

        # Deduplicar y limitar a 20
        seen = set()
        unique_skills = []
        for skill in skills:
            if skill.lower() not in seen:
                seen.add(skill.lower())
                unique_skills.append(skill)

        return unique_skills[:20]


    def _parse_experience_section(self, lines: List[str]) -> List[Dict]:
        """Extrae experiencia laboral de forma más precisa."""
        experience = []

        # Encontrar índice de la sección (maneja errores de OCR como "Experietnce")
        exp_start_idx = -1
        for i, line in enumerate(lines):
            if line.strip().startswith("Experi"):
                exp_start_idx = i
                break

        if exp_start_idx == -1:
            return []

        # Filtrar líneas de basura (caracteres únicos de OCR)
        def is_garbage(line):
            s = line.strip()
            if not s or len(s) <= 1:
                return True
            if s.startswith("Page "):
                return True
            if re.match(r"^[a-z]$", s):
                return True
            return False

        def clean_title(line):
            clean = line
            # Quitar prefijos de carácter único de OCR: "i Back End Developer" → "Back End Developer"
            clean = re.sub(r"^[a-z]\s+", "", clean)
            # Quitar sufijo de letra suelta: "Full Stack Engineer l" → "Full Stack Engineer"
            clean = re.sub(r'\s+[a-z]$', '', clean)
            # "Back End tDeveloper" → "Back End Developer"
            clean = re.sub(r'tDeveloper', 'Developer', clean)
            # "DBack End Developer" → "Back End Developer"
            if clean.startswith("D") and "Back" in clean:
                clean = clean[1:]
            return clean

        def clean_date(line):
            # Arreglar meses con letra de más: "Januaryd" → "January"
            line = re.sub(r'(January|February|March|April|May|June|July|August|September|October|November|December)d', r'\1', line)
            line = re.sub(r'(Enero|Febrero|Marzo|Abril|Mayo|Junio|Julio|Agosto|Septiembre|Octubre|Noviembre|Diciembre)d', r'\1', line)
            return line

        # Keywords para detectar títulos de puesto
        title_keywords = ["Developer", "Engineer", "Lead", "Senior", "Junior",
                          "Architect", "Manager", "Technical", "Full Stack",
                          "Back End", "Frontend", "Data", "Analyst", "Designer", "Leader"]

        location_keywords = ["Buenos Aires", "Greater Buenos", "Córdoba", 
                             "United States", "Argentina", "California", 
                             "San Francisco", "Province"]

        current_job = None
        current_description = []

        for i in range(exp_start_idx + 1, len(lines)):
            raw = lines[i]
            line = raw.strip()

            # Ignorar basura
            if is_garbage(line):
                continue

            # Detectar fin de experiencia
            if line.startswith("Education") or "ducation" in line:
                break

            # Ignorar ubicaciones
            if any(loc in line for loc in location_keywords) and len(line) < 60:
                continue

            # Detectar fecha: "May 2022 - Present (4 years 6 months)"
            if re.search(r"[A-Z][a-z]+ 20\d{2}\s*-\s*", line):
                line = clean_date(line)
                if current_job:
                    current_job["dates"] = line
                else:
                    current_job = {"company": "", "title": "", "dates": line, "description": ""}
                continue

            # Detectar bullets (pueden tener prefijo de carácter)
            bullet_match = re.match(r"^[a-z]?\s*[\*\-\u2022]\s+", line)
            if bullet_match:
                desc = line[bullet_match.end():].strip()
                if current_job:
                    current_description.append(desc)
                continue

            # Detectar Tools / Herramientas
            if line.startswith("Tools:") or line.startswith("Herramientas:"):
                if current_job:
                    current_description.append(line.replace("Tools:", "Tecnologías:"))
                continue

            # Detectar duración corta (ej: "4F years 6 months") - no es job ni title
            if re.search(r"\d+\s*(years?|años?|months?|meses?)", line, re.IGNORECASE) and \
               not any(kw in line for kw in title_keywords) and \
               not re.search(r"20\d{2}", line):
                continue

            # Detectar título de puesto
            if any(kw in line for kw in title_keywords):
                clean = clean_title(line)
                if current_job and current_job.get("title"):
                    # Ya tenemos título → nueva posición en misma empresa
                    if current_description:
                        current_job["description"] = " ".join(current_description).strip()
                        current_description = []
                    experience.append(current_job)
                    current_job = {"company": current_job.get("company", ""), "title": clean, "dates": "", "description": ""}
                elif current_job:
                    current_job["title"] = clean
                else:
                    current_job = {"company": "", "title": clean, "dates": "", "description": ""}
                continue

            # Detectar empresa
            if re.match(r"^[A-Z][a-zA-Z0-9\s&.]+$", line) and \
               len(line) > 3 and len(line) < 60 and \
               not any(kw in line for kw in title_keywords):
                if current_job and (current_job.get("title") or current_job.get("dates")):
                    if current_description:
                        current_job["description"] = " ".join(current_description).strip()
                        current_description = []
                    experience.append(current_job)
                current_job = {"company": line, "title": "", "dates": "", "description": ""}
                continue

            # Si no es ninguno de los anteriores, podría ser descripción continua
            if current_job and len(line) > 10:
                current_description.append(line)

        # Agregar último trabajo
        if current_job and (current_job.get("title") or current_job.get("company") or current_job.get("dates")):
            if current_description:
                current_job["description"] = " ".join(current_description).strip()
            experience.append(current_job)

        return experience[:5]

    def _parse_education_section(self, lines: List[str]) -> List[Dict]:
        """Extrae información educativa."""
        education = []

        # Encontrar sección de educación
        edu_start_idx = -1
        for i, line in enumerate(lines):
            if line.strip().startswith("Education"):
                edu_start_idx = i
                break

        if edu_start_idx == -1:
            return []

        # Extraer líneas de educación (filtrar basura)
        edu_lines = []
        for i in range(edu_start_idx + 1, len(lines)):
            line = lines[i].strip()
            if line.startswith("Page"):
                break
            # Ignorar basura (caracteres únicos)
            if not line or len(line) <= 1:
                continue
            # Ignorar líneas que son solo decoración
            if re.match(r"^[a-z]\s*[a-z]*$", line):
                continue
            edu_lines.append(line)

        if edu_lines:
            # La primera línea con texto largo es la institución
            institution = edu_lines[0] if edu_lines else ""
            degree = edu_lines[1] if len(edu_lines) > 1 else ""
            dates = edu_lines[2] if len(edu_lines) > 2 else ""

            education.append({
                "institution": institution,
                "degree": degree,
                "dates": dates
            })

        return education

    def _parse_languages(self, lines: List[str]) -> List[str]:
        """Extrae lenguas del perfil con nivel de proficiencia."""
        languages = []
        for line in lines:
            stripped = line.strip()
            # Match patterns like "Spanish (Native or Bilingual)", "English (Full Professional)"
            if "Native" in stripped or "Bilingual" in stripped or "Professional" in stripped:
                # Devolver el texto completo (idioma + nivel)
                languages.append(stripped)
        return list(dict.fromkeys(languages))  # Preserve order, deduplicate

    def _parse_summary_section(self, lines: List[str]) -> str:
        """Extrae el resumen profesional."""
        summary_lines = []
        in_summary = False

        # Conocer skills ya extraídas para excluirlas del resumen
        known_skills = set()
        if self.data.get("skills"):
            for s in self.data["skills"]:
                known_skills.add(s.lower())

        # Sección de parada: experiencia, educación, etc.
        stop_keywords = ["experience", "experietnce", "education", "eduction"]

        for i, line in enumerate(lines):
            stripped = line.strip()

            if not in_summary:
                if "(LinkedIn) Summary" in stripped:
                    in_summary = True
                continue

            # Detenerse al encontrar la sección de experiencia
            lower = stripped.lower()
            if any(kw in lower for kw in stop_keywords) and len(stripped) < 15:
                break
            if stripped.startswith("Top Skills"):
                # Top Skills no marca el fin del resumen - el texto continua
                continue
            if stripped.startswith("Education"):
                break

            # Filtrar basura: caracteres únicos, "r", "o", "e", etc.
            if not stripped or len(stripped) <= 1:
                continue
            if re.match(r"^[a-z]$", stripped):
                continue
            # Filtrar líneas que son solo decoración ("r", "o", etc.)
            if re.match(r"^[a-z]\s*[a-z]?s*$", stripped):
                continue
            # Filtrar líneas de "Page" 
            if stripped.startswith("Page "):
                break

            # Excluir nombres de skills ya identificados (están en su propia sección)
            if stripped.lower() in known_skills:
                continue

            # Agregar líneas significativas del resumen
            if len(stripped) > 5:
                summary_lines.append(stripped)

        return " ".join(summary_lines)

    def save_json(self, filename: str = "parsed_linkedin_profile.json"):
        """Guarda los datos parseados en formato JSON."""
        assets_dir = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "parsed_data")
        os.makedirs(assets_dir, exist_ok=True)

        output_path = os.path.join(assets_dir, filename)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)
        print(f"Datos guardados en: {output_path}")
        return output_path

    def get_summary_stats(self) -> Dict:
        """Devuelve estadísticas resumidas para la interfaz de usuario."""
        return {
            "name": self.data.get("name", ""),
            "headline": self.data.get("headline", ""),
            "skills_count": len(self.data.get("skills", [])),
            "experience_count": len(self.data.get("experience", [])),
            "education_count": len(self.data.get("education", [])),
            "languages_count": len(self.data.get("languages", [])),
            "has_summary": bool(self.data.get("summary", ""))
        }

if __name__ == "__main__":
    pdf_path = "/home/gerardo/projects/curriculum_custom/data/gerardobenittez_profile_linkedin.pdf"

    if not os.path.exists(pdf_path):
        print(f"Error: No se encuentra el archivo PDF en {pdf_path}")
        exit(1)

    parser = LinkedInPDFParser(pdf_path)

    print("Parseando PDF de LinkedIn...")
    data = parser.parse()

    print("\n=== RESULTADOS DEL PARSEO ===")
    print(json.dumps(data, indent=2, ensure_ascii=False))

    # Guardar resultados
    output_path = parser.save_json()
    print(f"\nDatos guardados en: {output_path}")

    # Mostrar estadísticas
    stats = parser.get_summary_stats()
    print("\n=== ESTADÍSTICAS ===")
    print(json.dumps(stats, indent=2, ensure_ascii=False))