"""Analizador de job descriptions usando OpenAI para extracción de información clave."""
import json
import os
from typing import Dict, List, Any
from openai import OpenAI
from dotenv import load_dotenv
import re

# Cargar variables de entorno
load_dotenv()

class JobAnalyzer:
    """Analiza job descriptions para extraer keywords, skills y requisitos usando IA."""
    
    def __init__(self):
        """Inicializa el analizador con cliente OpenAI."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key or api_key == "sk-tu-api-key-aqui":
            raise ValueError("⚠️ Configura tu OPENAI_API_KEY en el archivo .env")
        
        self.client = OpenAI(api_key=api_key)
    
    def _normalize_job_data(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normaliza keys del job_data para uso interno consistente (ES/EN → keys unificadas)."""
        # Extraer habilidades técnicas (ES tiene dict anidado, EN tiene list)
        tech_skills_raw = job_data.get('technical_skills') or job_data.get('habilidades_tecnicas', [])
        if isinstance(tech_skills_raw, dict):
            flat_skills = []
            for v in tech_skills_raw.values():
                if isinstance(v, list):
                    flat_skills.extend(v)
            tech_skills = flat_skills
        else:
            tech_skills = tech_skills_raw
        
        return {
            "title": job_data.get("title") or job_data.get("titulo_puesto") or job_data.get("job_title", ""),
            "seniority": (job_data.get("seniority") or job_data.get("nivel_seniority") or 
                         job_data.get("seniority_level") or ""),
            "technical_skills": tech_skills,
            "soft_skills": (job_data.get("soft_skills") or 
                           job_data.get("habilidades_blandas") or []),
            "requirements": (job_data.get("requirements") or 
                            job_data.get("requisitos_minimos") or []),
            "responsibilities": (job_data.get("responsibilities") or 
                                 job_data.get("responsabilidades_clave") or
                                 job_data.get("key_responsibilities") or []),
            "technologies_mentioned": (job_data.get("technologies_mentioned") or 
                                       job_data.get("tecnologias_mencionadas") or []),
            "benefits": (job_data.get("benefits") or 
                        job_data.get("bonus_beneficios") or []),
        }
    
    def analyze_job_description(self, job_text: str, language: str = "es") -> Dict[str, Any]:
        """
        Analiza una job description y extrae información estructurada.
        
        Args:
            job_text: Texto completo de la job description
            language: Idioma de salida - "es" o "en"
            
        Returns:
            Dict con información estructurada de la oferta
        """
        lang_instruction = "en español" if language == "es" else "in English"
        prompt = f"""
Eres un experto en recursos humanos y reclutamiento técnico. Analiza la siguiente job description y extrae la información en formato JSON estructurado. Responde {lang_instruction}.

Job Description:
{job_text[:3000]}

Extrae la siguiente información:
1. Título del puesto
2. Nivel de seniority (junior, mid, senior, lead, principal)
3. Habilidades técnicas requeridas (lenguajes de programación, frameworks, herramientas)
4. Habilidades blandas requeridas (soft skills)
5. Requisitos mínimos (education, certifications)
6. Responsabilidades clave
7. Tecnologías mencionadas
8. Bonus/beneficios mencionados

Devuelve solo el JSON, nada más.
"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system", 
                        "content": "Eres un especialista en análisis de ofertas de trabajo. Extraes información estructurada en formato JSON."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.3
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            print(f"❌ Error analizando job description: {e}")
            return self._fallback_analysis(job_text)
    
    def _fallback_analysis(self, job_text: str) -> Dict[str, Any]:
        """Análisis alternativo cuando falla la IA."""
        tech_keywords = [
            "python", "javascript", "typescript", "java", "react", "vue", "angular",
            "node.js", "nodejs", "fastapi", "django", "flask", "spring", "aws", 
            "docker", "kubernetes", "terraform", "git", "ci/cd", "mongodb", "postgres",
            "redis", "kafka", "rabbitmq", "celery", "pytest", "jest", "selenium",
            "machine learning", "tensorflow", "pytorch", "docker", "kubernetes"
        ]
        
        skills = []
        text_lower = job_text.lower()
        for keyword in tech_keywords:
            if keyword in text_lower:
                skills.append(keyword)
        
        return {
            "title": "",
            "seniority": "mid",
            "technical_skills": list(set(skills)),
            "soft_skills": [],
            "requirements": [],
            "responsibilities": [],
            "technologies_mentioned": list(set(skills)),
            "benefits": []
        }
    
    def generate_keyword_matching(self, profile_data: Dict, job_data: Dict, language: str = "es") -> Dict[str, float]:
        """
        Genera puntuación de matching entre perfil y job description.
        
        Args:
            profile_data: Datos del perfil (LinkedIn + GitHub)
            job_data: Datos analizados de la job description
            language: Idioma de respuesta - "es" o "en"
            
        Returns:
            Dict con puntuaciones de matching por categoría
        """
        lang_instruction = "responde en español" if language == "es" else "respond in English"
        prompt = f"""
Eres un experto en matching de perfiles profesionales. Evalúa qué tan bien coincide este perfil con los requisitos de la oferta de trabajo.

PERFIL DEL CANDIDATO:
Nombre: {profile_data.get('name', '')}
Headline: {profile_data.get('headline', '')}
Skills: {', '.join(profile_data.get('skills', []))}
Experiencia: {json.dumps(profile_data.get('experience', []))}
GitHub Lenguajes: {', '.join(profile_data.get('top_languages', []))}

REQUISITOS DE LA OFERTA:
Título: {job_data.get('title', '')}
Seniority: {job_data.get('seniority', '')}
Habilidades Técnicas: {', '.join(job_data.get('technical_skills', []))}
Responsabilidades: {', '.join(job_data.get('responsibilities', [])[:3])}

Evalúa cada categoría y proporciona una puntuación del 0-100:
- matching_skills: Qué porcentaje de habilidades técnicas coinciden
- matching_experience: Qué tan relevante es la experiencia
- matching_title: Qué tal coincide el título profesional
- matching_seniority: Coincidencia de nivel senior

Devuelve solo JSON con puntuaciones numéricas. {lang_instruction}.
"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system", 
                        "content": "Eres un experto en evaluación de matching profesional. Proporcionas puntuaciones numéricas precisas."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.2
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            print(f"❌ Error generando matching: {e}")
            return {
                "matching_skills": 50,
                "matching_experience": 50,
                "matching_title": 50,
                "matching_seniority": 50
            }
    
    def optimize_resume_content(self, profile_data: Dict, job_data: Dict, language: str = "es") -> Dict[str, Any]:
        """
        Genera contenido optimizado del CV basado en la job description.
        
        Args:
            profile_data: Datos completos del perfil
            job_data: Job description analizada
            language: Idioma de salida - "es" o "en"
            
        Returns:
            Dict con contenido optimizado para cada sección del CV
        """
        lang_instruction = "en español" if language == "es" else "in English"
        # Extraer habilidades clave del job
        job_skills = job_data.get('technical_skills', [])
        job_responsibilities = job_data.get('responsibilities', [])
        
        # Preparar datos del perfil
        current_skills = profile_data.get('skills', [])
        experience = profile_data.get('experience', [])
        
        prompt = f"""
Eres un experto en escritura de currículums técnicos. Optimiza el contenido del CV para pasar los filtros ATS y destacar el matching con esta oferta. Responde {lang_instruction}.

PERFIL ACTUAL:
Skills: {', '.join(current_skills)}
Experiencia: {json.dumps(experience)}

OFERTA REQUERIDA:
Título: {job_data.get('title', '')}
Seniority: {job_data.get('seniority', '')}
Skills requeridas: {', '.join(job_skills)}
Responsabilidades mencionadas: {', '.join(job_responsibilities[:5])}

Tareas:
1. Reescribe las habilidades técnicas para destacar las del job ({', '.join(job_skills)})
2. Reordena los skills poniendo primero los del job
3. Reescribe las experiencias laborales para usar keywords del job
4. Genera un resumen profesional enfocado en la oferta
5. Extrae logros cuantificables de tu experiencia

Devuelve JSON con:
- optimized_skills: skills reorder y destacadas
- optimized_summary: resumen profesional de 2-3 líneas
- optimized_experience: experiencia con keywords del job
- ats_keywords: lista de keywords extraídas del job para incluir

"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system", 
                        "content": "Eres un especialista en optimización de currículums para ATS. Maximizas el matching keyword con ofertas de trabajo."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.4
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            print(f"❌ Error optimizando contenido: {e}")
            return {
                "optimized_skills": current_skills,
                "optimized_summary": profile_data.get('summary', ''),
                "optimized_experience": experience,
                "ats_keywords": job_skills
            }
    
    def save_analysis(self, analysis: Dict, filename: str = "job_analysis.json"):
        """Guarda el análisis en archivo JSON."""
        output_dir = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "parsed_data")
        os.makedirs(output_dir, exist_ok=True)
        
        output_path = os.path.join(output_dir, filename)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False, default=str)
        print(f"Análisis guardado en: {output_path}")
        return output_path

if __name__ == "__main__":
    # Prueba rápida
    try:
        analyzer = JobAnalyzer()
        
        sample_job = """
        Senior Backend Engineer
        
        Buscamos ingeniero backend con experiencia en Python, FastAPI, AWS, Docker, PostgreSQL.
        
        Responsabilidades:
        - Desarrollar APIs REST
        - Trabajar con arquitectura serverless
        - Implementar pruebas unitarias
        
        Requisitos:
        - 5+ años de experiencia
        - Conocimiento en CI/CD
        - Experiencia con microservicios
        """
        
        print("Analizando job description...")
        result = analyzer.analyze_job_description(sample_job)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
    except ValueError as e:
        print(e)
    except Exception as e:
        print(f"Error: {e}")