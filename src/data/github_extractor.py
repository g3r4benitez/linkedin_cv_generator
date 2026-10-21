"""Extractor de información de GitHub para complementar el perfil profesional."""
import os
import json
from typing import Dict, List, Any, Optional
from github import Github
from datetime import datetime, timedelta

class GitHubExtractor:
    """Extrae información relevante de un perfil de GitHub para CV."""
    
    def __init__(self, token: Optional[str] = None):
        """
        Inicializa el extractor de GitHub.
        
        Args:
            token: Token de acceso personal de GitHub (opcional pero recomendado)
        """
        self.client = None
        if token:
            self.client = Github(token)
    
    def extract_profile(self, username: str) -> Dict[str, Any]:
        """
        Extrae información completa del perfil de GitHub.
        
        Args:
            username: Nombre de usuario de GitHub
            
        Returns:
            Dict con información estructurada del perfil
        """
        profile_data = {
            "username": username,
            "name": "",
            "bio": "",
            "location": "",
            "company": "",
            "blog": "",
            "public_repos": 0,
            "followers": 0,
            "following": 0,
            "created_at": "",
            "updated_at": "",
            "top_languages": [],
            "featured_repos": [],
            "recent_activity": [],
            "contributions_last_year": 0,
            "repositories": []
        }
        
        try:
            if not self.client:
                raise ValueError("Se requiere un token de GitHub para esta operación")
            
            user = self.client.get_user(username)
            
            # Información básica
            profile_data["name"] = user.name or ""
            profile_data["bio"] = user.bio or ""
            profile_data["location"] = user.location or ""
            profile_data["company"] = user.company or ""
            profile_data["blog"] = user.blog or ""
            profile_data["public_repos"] = user.public_repos
            profile_data["followers"] = user.followers
            profile_data["following"] = user.following
            profile_data["created_at"] = user.created_at.isoformat() if user.created_at else ""
            profile_data["updated_at"] = user.updated_at.isoformat() if user.updated_at else ""
            
            print(f"✅ Perfil encontrado: {profile_data['name']} ({username})")
            
            # Extraer lenguajes y repositorios
            languages_count = {}
            repos = []
            
            for repo in user.get_repos(sort="stars", direction="desc")[:20]:
                try:
                    repo_data = {
                        "name": repo.name,
                        "full_name": repo.full_name,
                        "description": repo.description or "",
                        "language": repo.language or "",
                        "stars": repo.stargazers_count,
                        "forks": repo.forks_count,
                        "created_at": repo.created_at.isoformat() if repo.created_at else "",
                        "updated_at": repo.updated_at.isoformat() if repo.updated_at else "",
                        "url": repo.html_url,
                        "is_fork": repo.fork,
                        "size": repo.size,
                        "open_issues": repo.open_issues_count,
                        "license": repo.get_license().license.name if repo.get_license() else ""
                    }
                    
                    repos.append(repo_data)
                    
                    # Contar lenguajes
                    if repo.language:
                        lang = repo.language
                        languages_count[lang] = languages_count.get(lang, 0) + 1
                    
                    # Extraer lenguajes específicos del repositorio
                    try:
                        languages = repo.get_languages()
                        for lang, bytes_count in languages.items():
                            languages_count[lang] = languages_count.get(lang, 0) + 1
                    except:
                        pass
                    
                except Exception as e:
                    print(f"⚠️ Error procesando repositorio {repo.name}: {e}")
                    continue
            
            profile_data["repositories"] = repos
            
            # Top lenguajes por uso
            sorted_languages = sorted(languages_count.items(), key=lambda x: x[1], reverse=True)
            profile_data["top_languages"] = [lang for lang, count in sorted_languages[:10]]
            
            # Repositorios destacados (por estrellas, no forks, con descripción)
            featured = [
                repo for repo in repos 
                if repo["stars"] > 0 and not repo["is_fork"] and repo["language"]
            ][:5]
            profile_data["featured_repos"] = featured
            
            # Actividad reciente (últimos 30 días)
            profile_data["recent_activity"] = self._extract_recent_activity(username)
            
            # Estimación de contribuciones (basada en commits de repos públicos)
            profile_data["contributions_last_year"] = self._estimate_contributions(user)
            
            return profile_data
            
        except Exception as e:
            print(f"❌ Error extrayendo perfil de GitHub: {e}")
            return profile_data
    
    def _extract_recent_activity(self, username: str) -> List[Dict]:
        """Extrae actividad reciente (últimos 30 días)."""
        activity = []
        try:
            user = self.client.get_user(username)
            events = user.get_events()
            
            thirty_days_ago = datetime.now() - timedelta(days=30)
            
            for event in events[:30]:  # Últimos 30 eventos
                try:
                    if event.created_at and event.created_at.replace(tzinfo=None) > thirty_days_ago:
                        activity_data = {
                            "type": event.type,
                            "repo": event.repo.name if event.repo else "",
                            "created_at": event.created_at.isoformat() if event.created_at else "",
                            "payload": {}
                        }
                        
                        # Extraer información relevante según tipo de evento
                        if event.type == "PushEvent":
                            commits_count = event.payload.get("size", 0)
                            activity_data["payload"] = {
                                "commits": commits_count,
                                "repo": event.repo.name
                            }
                        elif event.type == "CreateEvent":
                            activity_data["payload"] = {
                                "ref_type": event.payload.get("ref_type", ""),
                                "ref": event.payload.get("ref", "")
                            }
                        
                        activity.append(activity_data)
                except Exception:
                    continue
                    
        except Exception as e:
            print(f"⚠️ Error extrayendo actividad reciente: {e}")
        
        return activity
    
    def _estimate_contributions(self, user) -> int:
        """Estima el número de contribuciones basado en actividad pública."""
        total_commits = 0
        try:
            repos = user.get_repos()
            for repo in repos[:10]:  # Limitar a 10 repositorios
                try:
                    # Contar commits en los últimos 12 meses
                    commits = repo.get_commits(since=datetime.now() - timedelta(days=365))
                    # Contar sin iterar todos (aproximado)
                    total_commits += min(commits.totalCount, 200)  # Cap para evitar tiempo excesivo
                except:
                    continue
        except:
            pass
        
        return total_commits
    
    def generate_github_highlights(self, profile_data: Dict) -> Dict[str, Any]:
        """
        Genera highlights de GitHub para incluir en el CV.
        
        Returns:
            Dict con proyectos destacados y estadísticas relevantes
        """
        highlights = {
            "total_repos": profile_data.get("public_repos", 0),
            "total_followers": profile_data.get("followers", 0),
            "top_languages": profile_data.get("top_languages", [])[:5],
            "featured_projects": [],
            "recent_contributions": profile_data.get("contributions_last_year", 0)
        }
        
        # Formatear repositorios destacados para CV
        for repo in profile_data.get("featured_repos", [])[:3]:
            if repo:
                highlights["featured_projects"].append({
                    "name": repo.get("name", ""),
                    "description": repo.get("description", ""),
                    "language": repo.get("language", ""),
                    "stars": repo.get("stars", 0),
                    "url": repo.get("url", "")
                })
        
        return highlights
    
    def save_json(self, data: Dict, filename: str = "github_profile_data.json"):
        """Guarda los datos extraídos en un archivo JSON."""
        output_dir = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "parsed_data")
        os.makedirs(output_dir, exist_ok=True)
        
        output_path = os.path.join(output_dir, filename)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        print(f"Datos de GitHub guardados en: {output_path}")
        return output_path

if __name__ == "__main__":
    # Ejemplo de uso
    # Nota: Reemplaza 'tu-token-github' con tu token real
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
    
    if not GITHUB_TOKEN:
        print("❌ Por favor configura GITHUB_TOKEN en tu archivo .env")
        print("   Puedes obtenerlo desde: https://github.com/settings/tokens")
    else:
        extractor = GitHubExtractor(token=GITHUB_TOKEN)
        
        # Extraer perfil
        profile_data = extractor.extract_profile("gerardobenitez")
        
        # Guardar datos
        extractor.save_json(profile_data)
        
        # Generar highlights para CV
        highlights = extractor.generate_github_highlights(profile_data)
        
        print("\n=== HIGHLIGHTS DE GITHUB PARA CV ===")
        print(json.dumps(highlights, indent=2, ensure_ascii=False))