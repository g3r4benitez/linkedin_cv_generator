"""Generador de currículums optimizados usando IA y plantillas ATS-friendly."""
import json
import os
import sys
from typing import Dict, List, Any
from jinja2 import Template
from datetime import datetime

# Agregar el directorio raíz al path para imports absolutos
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from src.ai.job_analyzer import JobAnalyzer

class ResumeGenerator:
    """Genera currículums optimizados basados en perfiles y job descriptions."""

    def __init__(self):
        self.job_analyzer = None
        self.template = None
        try:
            self.job_analyzer = JobAnalyzer()
        except ValueError:
            print("⚠️ OpenAI API key no configurada. Funcionará sin optimización con IA.")
        self._load_template()

    def _load_template(self):
        """Carga la plantilla HTML ATS-friendly."""
        template_path = os.path.join(
            os.path.dirname(__file__), 
            "..", "..", "src", "templates", "ats_template.html"
        )

        # Template base ATS-friendly
        self.template = Template("""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ name }} - Currículum Profesional</title>
    <style>
        body {
            font-family: 'Arial', sans-serif;
            line-height: 1.4;
            color: #333;
            max-width: 900px;
            margin: 0 auto;
            padding: 15px;
            font-size: 12px;
        }
        @page { margin: 0.5in; size: letter; }
        .header {
            text-align: center;
            margin-bottom: 15px;
            border-bottom: 2px solid #4A90E2;
            padding-bottom: 10px;
        }
        .header h1 {
            margin: 0;
            font-size: 22px;
            color: #2C3E50;
        }
        .header h2 {
            margin: 3px 0;
            color: #7F8C8D;
            font-size: 14px;
        }
        .contact-info {
            margin-top: 8px;
            font-size: 12px;
        }
        .section {
            margin-bottom: 12px;
        }
        .section h3 {
            color: #4A90E2;
            border-bottom: 1px solid #BDC3C7;
            padding-bottom: 3px;
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .job-item {
            margin-bottom: 8px;
        }
        .job-title {
            font-weight: bold;
            color: #2C3E50;
            font-size: 14px;
        }
        .job-dates {
            color: #7F8C8D;
            font-size: 12px;
        }
        .skills-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
            gap: 4px;
            margin-top: 5px;
        }
        .skill-item {
            padding: 3px 3px;
            font-size: 10px;
        }
        .achievement {
            font-size: 10px;
            margin-left: 10px;
        }
        .target-role {
            font-size: 11px;
            color: #4A90E2;
            margin-top: 5px;
        }
    </style>
</head>
<body>
    <!-- Header -->
    <div class="header">
        <h1>{{ name }}</h1>
        <h2>{{ headline }}</h2>
        <div class="contact-info">
            {% if contact_info.email %}📧 {{ contact_info.email }} | {% endif %}
            {% if contact_info.phone %}📱 {{ contact_info.phone }} | {% endif %}
            {% if contact_info.location %}📍 {{ contact_info.location }} | {% endif %}
            {% if github_url %}🔗 <a href="{{ github_url }}">GitHub: @{{ github_username }}</a>{% endif %}
        </div>
    </div>


    <!-- Target Role (from job description) -->
    {% if target_role %}
    <div class="section">
        <p style="font-size:14px; color:#4A90E2; margin-top:5px;">🎯 {{ labels.target }}: {{ target_role }}</p>
    </div>
    {% endif %}

    <!-- Professional Summary -->
    {% if summary %}
    <div class="section">
        <h3>{{ labels.summary }}</h3>
        <p>{{ summary }}</p>
    </div>
    {% endif %}

    <!-- Skills -->
    <div class="section">
        <h3>{{ labels.skills }}</h3>
        <div >
            {% for skill in skills %}
            <span class="skill-item">{{ skill }}</span>
            {% endfor %}
        </div>
    </div>

    <!-- Experience -->
    <div class="section">
        <h3>{{ labels.experience }}</h3>
        {% for job in experience %}
        <div class="job-item">
            <div class="job-title">{{ job.title }} at {{ job.company }} | <span class="job-dates">{{ job.dates }}</span></div>
            {% if job.description %}
            <p style="font-size:13px; margin-top:5px;">{{ job.description if job.description is string else job.description }}</p>
            {% endif %}
    <!-- Skills -->
    <div class="section">
        <h3>{{ labels.skills }}</h3>
        </div>
        {% endfor %}
    </div>

    <!-- Education -->
    {% if education %}
    <div class="section">
        <h3>{{ labels.education }}</h3>
        {% for edu in education %}
        <div class="job-item">
            <div class="job-title">{{ edu.institution }}</div>
            <div class="job-dates">{{ edu.degree }} | {{ edu.dates }}</div>
        </div>
        {% endfor %}
    </div>
    {% endif %}

    <!-- Languages -->
    {% if languages %}
    <div class="section">
        <h3>{{ labels.languages }}</h3>
        <div style="display: flex; gap: 15px; flex-wrap: wrap;">
            {% for lang in languages %}
            <span style="font-size: 11px;">{{ lang }}</span>
            {% endfor %}
        </div>
    </div>
    {% endif %}

    <!-- Skills -->
    <div class="section">
        <h3>{{ labels.skills }}</h3>
    <!-- GitHub Highlights -->
    {% if github_highlights.featured_projects %}
    <div class="section">
        <h3>{{ labels.github }}</h3>
        {% for project in github_highlights.featured_projects %}
        <div class="job-item">
            <div class="job-title">{{ project.name }}</div>
            <div class="job-dates">{{ project.language }} | ⭐ {{ project.stars }} stars</div>
            {% if project.description %}
            <p style="font-size:13px;">{{ project.description }}</p>
            {% endif %}
        </div>
        {% endfor %}
    </div>
    {% endif %}
</body>
</html>
""")

    def _get_labels(self, language: str = "es") -> Dict[str, str]:
        """Devuelve las etiquetas de sección según el idioma."""
        if language == "en":
            return {
                "summary": "PROFESSIONAL SUMMARY",
                "skills": "TECHNICAL SKILLS",
                "experience": "PROFESSIONAL EXPERIENCE",
                "education": "EDUCATION",
                "github": "OPEN SOURCE CONTRIBUTIONS",
                "languages": "LANGUAGES",
                "target": "Target Role",
                "contact": "Contact:",
            }
        return {
            "summary": "PERFIL PROFESIONAL",
            "skills": "HABILIDADES TÉCNICAS",
            "experience": "EXPERIENCIA PROFESIONAL",
            "education": "EDUCACIÓN",
            "github": "CONTRIBUCIONES OPEN SOURCE",
            "languages": "IDIOMAS",
            "target": "Puesto Objetivo",
            "contact": "Contacto:",
        }

    def generate_resume(self, profile_data: Dict, job_description: str = None, use_ai: bool = True, language: str = "es") -> str:
        """
        Genera un currículum HTML optimizado.

        Args:
            profile_data: Datos combinados (LinkedIn + GitHub)
            job_description: Texto de la job description (opcional)
            use_ai: Habilitar optimización con IA (requiere API key)
            language: Idioma de salida - "es" (español) o "en" (inglés)

        Returns:
            HTML del currículum generado
        """
        # Traducir etiquetas según idioma
        labels = self._get_labels(language)

        try:
            # Si hay job description, optimizar contenido con IA
            if job_description and use_ai and self.job_analyzer:
                job_data = self.job_analyzer.analyze_job_descrip
    <!-- Skills -->
    <div class="section">
        <h3>{{ labels.skills }}</h3>tion(job_description, language)
                job_data = self.job_analyzer._normalize_job_data(job_data)
                optimized = self.job_analyzer.optimize_resume_content(profile_data, job_data, language)

                # Usar datos optimizados
                template_data = {
                    "name": profile_data.get("name", ""),
                    "headline": profile_data.get("headline", "")[:150],
                    "target_role": job_data.get("title", ""),
                    "contact_info": profile_data.get("contact_info", {}),
                    "summary": optimized.get("optimized_summary", profile_data.get("summary", "")),
                    "skills": optimized.get("optimized_skills", profile_data.get("skills", [])),
                    "experience": optimized.get("optimized_experience", profile_data.get("experience", [])),
                    "education": profile_data.get("education", []),
                    "languages": profile_data.get("languages", []),
                    "github_url": f"https://github.com/{profile_data.get('github_username', '')}",
                    "github_username": profile_data.get("github_username", ""),
                    "github_highlights": profile_data.get("github_highlights", {}),
                    "labels": labels
                }
            else:
                # Template base sin optimización
                template_data = {
                    "name": profile_data.get("name", ""),
                    "headline": profile_data.get("headline", "")[:150],
                    "target_role": profile_data.get("target_role", ""),
                    "contact_info": profile_data.get("contact_info", {}),
                    "summary": profile_data.get("summary", ""),
                    "skills": profile_data.get("skills", []),
                    "experience": profile_data.get("experience", []),
                    "education": profile_data.get("education", []),
                    "languages": profile_data.get("languages", []),
                    "github_url": f"https://github.com/{profile_data.get('github_username', '')}",
                    "github_username": profile_data.get("github_username", ""),
                    "github_highlights": profile_data.get("github_highlights", {}),
                    "labels": labels
                }
        except Exception as e:
            print(f"⚠️ Error en optimización con IA: {e}. Usando datos base.")
            template_data = {
                "name": profile_data.get("name", ""),
                "headline": profile_data.get("headline", "")[:150],
                "target_role": profile_data.get("target_role", ""),
                "contact_info": profile_data.get("contact_info", {}),
                "summary": profile_data.get("summary", ""),
                "skills": profile_data.get("skills", []),
                "experience": profile_data.get("experience", []),
                "education": profile_data.get("education", []),
                "languages": profile_data.get("languages", []),
                "github_url": f"https://github.com/{profile_data.get('github_username', '')}",
                "github_username": profile_data.get("github_username", ""),
                "github_highlights": profile_data.get("github_highlights", {}),
                "labels": labels
            }

        return self.template.render(**template_data)

    def generate_html_resume(self, profile_data: Dict, job_description: str = None, use_ai: bool = True, language: str = "es") -> str:
        """Genera versión en HTML del currículum."""
        return self.generate_resume(profile_data, job_description, use_ai, language)

    def save_resume(self, html_content: str, output_format: str = "html", filename: str = None) -> str:
        """
        Guarda el currículum en el formato solicitado.

        Args:
            html_content: HTML del currículum
            output_format: "html", "pdf", o "txt"
            filename: Nombre del archivo (opcional)

        Returns:
            Ruta donde se guardó el archivo
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            if output_format == "html":
                filename = f"cv_generado_{timestamp}.html"
            elif output_format == "pdf":
                filename = f"cv_generado_{timestamp}.pdf"
            elif output_format == "txt":
                filename = f"cv_generado_{timestamp}.txt"
            else:
                filename = f"cv_generado_{timestamp}.html"
)
        # Guardar en carpeta cvs_generados
        output_dir = os.path.join(os.path.dirname(__file__), "..", "..", "cvs_generados")
        os.makedirs(output_dir, exist_ok=True)

        output_path = os.path.join(output_dir, filename)

        if output_format == "html":
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(html_content)

        elif output_format == "pdf":
            try:
                import weasyprint

                # Configuración PDF profesional
                pdf_config = weasyprint.HTML(string=html_content)

                # Generar PDF con configuración
                pdf_config.write_pdf(
                    output_path,
                    presentational_hints=True,
                    stylesheets=[
                        weasyprint.CSS(string='@page { margin: 2cm; size: letter; }')
                    ]
                )

            except ImportError:
                print("⚠️ WeasyPrint no disponible. Guardando como HTML.")
                output_path += ".html"
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(html_content)
            except Exception as e:
                print(f"⚠️ Error generando PDF: {e}. Guardando como HTML.")
                output_path += ".html"
                # Forzar extensión HTML
                if output_path.endswith(".pdf"):
                    output_path = output_path.replace(".pdf", ".html")
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(html_content)

        elif output_format == "txt":
            # Extraer texto plano del HTML
            import re
            text_content = re.sub(r'<[^>]+>', ' ', html_content)
            text_content = re.sub(r'\s+', ' ', text_content).strip()

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(text_content)

        else:
            raise ValueError(f"Formato no soportado: {output_format}")

        print(f"Currículum guardado en: {output_path}")
        return output_path

    def generate_multiple_formats(self, profile_data: Dict, job_description: str = None) -> Dict[str, str]:
        """
        Genera el currículum en múltiples formatos.

        Args:
            profile_data: Datos del perfil
            job_description: Texto de la job description (opcional)

        Returns:
            Dict con rutas de archivos generados
        """
        html_resume = self.generate_resume(profile_data, job_description)

        outputs = {
            "html": self.save_resume(html_resume, "html", "cv_optimizado.html"),
        }

        # Intentar generar PDF
        try:
            outputs["pdf"] = self.save_resume(html_resume, "pdf", "cv_optimizado.pdf")
        except Exception as e:
            print(f"⚠️ No se pudo generar PDF: {e}")
            outputs["pdf"] = None

        return outputs

    def generate_multiple_versions(self, profile_data: Dict, job_descriptions: List[str]) -> List[str]:
        """Genera múltiples versiones del CV para diferentes ofertas."""
        resumes = []

        # Versión base (sin job description específica)
        base_html = self.generate_resume(profile_data)
        base_path = self.save_resume(base_html, "html", "cv_base.html")
        resumes.append(base_path)

        # Versiones optimizadas por job description
        for i, job_desc in enumerate(job_descriptions):
            optimized_html = self.generate_resume(profile_data, job_desc)
            path = self.save_resume(optimized_html, "html", f"cv_optimized_{i+1}.html")
            resumes.append(path)

        return resumes

if __name__ == "__main__":
    # Prueba rápida
    try:
        # Cargar datos de prueba
        profile_path = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "parsed_data", "parsed_linkedin_profile.json")

        if os.path.exists(profile_path):
            with open(profile_path, "r", encoding="utf-8") as f:
                profile_data = json.load(f)

            generator = ResumeGenerator()

            # Generar CV base
            html_resume = generator.generate_html_resume(profile_data)
            output_path = generator.save_resume(html_resume, "html", "cv_prueba.html")

            print(f"✅ Currículum de prueba generado: {output_path}")
        else:
            print("⚠️ No se encontraron datos de perfil. Primero ejecuta el parser de LinkedIn.")

    except Exception as e:
        print(f"Error en generación de CV: {e}")