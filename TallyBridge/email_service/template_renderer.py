"""
Email Template Renderer
Jinja2-based HTML template rendering
"""

import os
from jinja2 import Environment, FileSystemLoader, select_autoescape, TemplateNotFound
from typing import Dict, Any, Optional
from email_service.config import email_settings
import logging

logger = logging.getLogger(__name__)


class TemplateRenderer:
    """Jinja2 template renderer for emails"""
    
    def __init__(self, template_dir: Optional[str] = None):
        self.template_dir = template_dir or email_settings.TEMPLATE_DIR
        self._ensure_template_dir()
        
        self.env = Environment(
            loader=FileSystemLoader(self.template_dir),
            autoescape=select_autoescape(['html', 'xml']),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Add custom filters
        self.env.filters['format_date'] = self._format_date
        self.env.filters['format_currency'] = self._format_currency
    
    def _ensure_template_dir(self):
        """Ensure template directory exists"""
        if not os.path.exists(self.template_dir):
            os.makedirs(self.template_dir)
            logger.info(f"Created template directory: {self.template_dir}")
    
    @staticmethod
    def _format_date(value, format='%Y-%m-%d'):
        """Format date filter"""
        if hasattr(value, 'strftime'):
            return value.strftime(format)
        return str(value)
    
    @staticmethod
    def _format_currency(value, currency='INR'):
        """Format currency filter"""
        try:
            return f"{currency} {float(value):,.2f}"
        except:
            return str(value)
    
    def render(self, template_name: str, context: Dict[str, Any]) -> str:
        """
        Render template with context
        
        Args:
            template_name: Template filename (e.g., 'welcome.html')
            context: Dictionary of template variables
            
        Returns:
            Rendered HTML string
        """
        try:
            template = self.env.get_template(template_name)
            return template.render(**context)
        except TemplateNotFound:
            logger.error(f"Template not found: {template_name}")
            raise
        except Exception as e:
            logger.error(f"Template render error: {e}")
            raise
    
    def template_exists(self, template_name: str) -> bool:
        """Check if template exists"""
        try:
            self.env.get_template(template_name)
            return True
        except TemplateNotFound:
            return False


# Global instance
template_renderer = TemplateRenderer()


def render_email(template_name: str, context: Dict[str, Any]) -> str:
    """Render email template helper"""
    return template_renderer.render(template_name, context)
