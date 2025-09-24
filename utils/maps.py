"""
Utilitaires pour la gestion des cartes Folium dans ImoMatch
"""
import folium
from folium import plugins
import logging
from typing import List, Dict, Any, Tuple, Optional
import json

from config.settings import MAP_CONFIG, COLORS

logger = logging.getLogger(__name__)

class MapManager:
    """Gestionnaire pour les cartes interactives"""
    
    def __init__(self):
        self.default_location = MAP_CONFIG['default_location']
        self.default_zoom = MAP_CONFIG['default_zoom']
        self.marker_colors = MAP_CONFIG['marker_colors']
    
    def create_properties_map(self, properties: List[Dict[str, Any]], 
                             center: Tuple[float, float] = None,
                             zoom: int = None) -> folium.Map:
        """
        Crée une carte avec des propriétés
        
        Args:
            properties: Liste des propriétés à afficher
            center: Centre de la carte (lat, lng)
            zoom: Niveau de zoom
            
        Returns:
            folium.Map: Carte avec les propriétés
        """
        try:
            # Configuration de la carte
            map_center = center or self.default_location
            map_zoom = zoom or self.default_zoom
            
            # Créer la carte de base
            m = folium.Map(
                location=map_center,
                zoom_start=map_zoom,
                tiles='OpenStreetMap',
                prefer_canvas=True
            )
            
            # Ajouter les tuiles alternatives
            self._add_tile_layers(m)
            
            # Ajouter les propriétés
            if properties:
                self._add_properties_to_map(m, properties)
                
                # Ajuster la vue pour inclure toutes les propriétés
                if len(properties) > 1:
                    self._fit_bounds_to_properties(m, properties)
            
            # Ajouter les contrôles
            self._add_map_controls(m)
            
            return m
            
        except Exception as e:
            logger.error(f"Erreur création carte propriétés: {e}")
            return self._create_fallback_map()
    
    def create_search_area_map(self, center: Tuple[float, float], 
                              radius_km: float) -> folium.Map:
        """
        Crée une carte avec une zone de recherche circulaire
        
        Args:
            center: Centre de la zone de recherche
            radius_km: Rayon en kilomètres
            
        Returns:
            folium.Map: Carte avec la zone de recherche
        """
        try:
            m = folium.Map(
                location=center,
                zoom_start=self._calculate_zoom_for_radius(radius_km),
                tiles='OpenStreetMap'
            )
            
            # Ajouter le cercle de recherche
            folium.Circle(
                location=center,
                radius=radius_km * 1000,  # Conversion km -> mètres
                popup=f'Zone de recherche: {radius_km}km',
                color=COLORS['primary'],
                fillColor=COLORS['primary'],
                fillOpacity=0.2,
                opacity=0.8,
                weight=2
            ).add_to(m)
            
            # Ajouter un marker au centre
            folium.Marker(
                location=center,
                popup='Centre de recherche',
                tooltip='Zone de recherche',
                icon=folium.Icon(color='red', icon='crosshairs', prefix='fa')
            ).add_to(m)
            
            self._add_map_controls(m)
            
            return m
            
        except Exception as e:
            logger.error(f"Erreur création carte zone recherche: {e}")
            return self._create_fallback_map()
    
    def create_heatmap(self, properties: List[Dict[str, Any]], 
                      weight_field: str = 'price') -> folium.Map:
        """
        Crée une heatmap des propriétés
        
        Args:
            properties: Liste des propriétés
            weight_field: Champ à utiliser pour le poids ('price', 'surface', etc.)
            
        Returns:
            folium.Map: Carte avec heatmap
        """
        try:
            if not properties:
                return self._create_fallback_map()
            
            # Préparer les données pour la heatmap
            heat_data = []
            valid_properties = []
            
            for prop in properties:
                if prop.get('latitude') and prop.get('longitude'):
                    lat, lng = prop['latitude'], prop['longitude']
                    weight = prop.get(weight_field, 1)
                    
                    # Normaliser le poids selon le champ
                    if weight_field == 'price':
                        weight = weight / 100000  # Normaliser les prix
                    elif weight_field == 'surface':
                        weight = weight / 100  # Normaliser les surfaces
                    
                    heat_data.append([lat, lng, weight])
                    valid_properties.append(prop)
            
            if not heat_data:
                return self._create_fallback_map()
            
            # Calculer le centre
            center = self._calculate_center(valid_properties)
            
            # Créer la carte
            m = folium.Map(
                location=center,
                zoom_start=self.default_zoom,
                tiles='cartodbpositron'  # Fond plus clair pour la heatmap
            )
            
            # Ajouter la heatmap
            plugins.HeatMap(
                heat_data,
                min_opacity=0.2,
                max_zoom=18,
                radius=15,
                blur=10,
                gradient={
                    0.0: 'blue',
                    0.4: 'cyan', 
                    0.6: 'lime',
                    0.8: 'yellow',
                    1.0: 'red'
                }
            ).add_to(m)
            
            # Ajuster la vue
            self._fit_bounds_to_properties(m, valid_properties)
            
            return m
            
        except Exception as e:
            logger.error(f"Erreur création heatmap: {e}")
            return self._create_fallback_map()
    
    def create_cluster_map(self, properties: List[Dict[str, Any]]) -> folium.Map:
        """
        Crée une carte avec clustering des markers
        
        Args:
            properties: Liste des propriétés
            
        Returns:
            folium.Map: Carte avec clustering
        """
        try:
            if not properties:
                return self._create_fallback_map()
            
            # Calculer le centre
            center = self._calculate_center(properties)
            
            # Créer la carte
            m = folium.Map(
                location=center,
                zoom_start=self.default_zoom,
                tiles='OpenStreetMap'
            )
            
            # Créer le cluster
            marker_cluster = plugins.MarkerCluster().add_to(m)
            
            # Ajouter les propriétés au cluster
            for prop in properties:
                if prop.get('latitude') and prop.get('longitude'):
                    self._add_property_marker(marker_cluster, prop)
            
            # Ajuster la vue
            self._fit_bounds_to_properties(m, properties)
            
            self._add_map_controls(m)
            
            return m
            
        except Exception as e:
            logger.error(f"Erreur création carte cluster: {e}")
            return self._create_fallback_map()
    
    def create_comparison_map(self, properties: List[Dict[str, Any]]) -> folium.Map:
        """
        Crée une carte pour comparer plusieurs propriétés
        
        Args:
            properties: Liste des propriétés à comparer (max 5)
            
        Returns:
            folium.Map: Carte de comparaison
        """
        try:
            if not properties:
                return self._create_fallback_map()
            
            # Limiter à 5 propriétés pour la lisibilité
            properties = properties[:5]
            
            # Calculer le centre
            center = self._calculate_center(properties)
            
            # Créer la carte
            m = folium.Map(
                location=center,
                zoom_start=self.default_zoom,
                tiles='OpenStreetMap'
            )
            
            # Couleurs pour la comparaison
            comparison_colors = ['red', 'blue', 'green', 'purple', 'orange']
            
            # Ajouter chaque propriété avec une couleur distincte
            for i, prop in enumerate(properties):
                if prop.get('latitude') and prop.get('longitude'):
                    color = comparison_colors[i % len(comparison_colors)]
                    
                    # Marker avec numéro
                    folium.Marker(
                        location=[prop['latitude'], prop['longitude']],
                        popup=self._create_comparison_popup(prop, i + 1),
                        tooltip=f"Propriété {i + 1}: {prop['title'][:30]}...",
                        icon=folium.Icon(
                            color=color,
                            icon='home',
                            prefix='fa'
                        )
                    ).add_to(m)
                    
                    # Cercle coloré autour
                    folium.Circle(
                        location=[prop['latitude'], prop['longitude']],
                        radius=200,
                        color=color,
                        fillColor=color,
                        fillOpacity=0.1,
                        weight=2
                    ).add_to(m)
            
            # Ajuster la vue
            self._fit_bounds_to_properties(m, properties)
            
            # Légende
            self._add_comparison_legend(m, properties, comparison_colors)
            
            return m
            
        except Exception as e:
            logger.error(f"Erreur création carte comparaison: {e}")
            return self._create_fallback_map()
    
    # === MÉTHODES PRIVÉES ===
    
    def _add_tile_layers(self, m: folium.Map):
        """Ajoute des couches de tuiles alternatives"""
        try:
            # Satellite
            folium.TileLayer(
                tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
                attr='Esri',
                name='Satellite',
                overlay=False,
                control=True
            ).add_to(m)
            
            # Terrain
            folium.TileLayer(
                tiles='https://stamen-tiles-{s}.a.ssl.fastly.net/terrain/{z}/{x}/{y}{r}.png',
                attr='Stamen',
                name='Terrain',
                overlay=False,
                control=True
            ).add_to(m)
            
            # Contrôle des couches
            folium.LayerControl().add_to(m)
            
        except Exception as e:
            logger.error(f"Erreur ajout couches tuiles: {e}")
    
    def _add_properties_to_map(self, m: folium.Map, properties: List[Dict[str, Any]]):
        """Ajoute les propriétés à la carte"""
        for prop in properties:
            if prop.get('latitude') and prop.get('longitude'):
                self._add_property_marker(m, prop)
    
    def _add_property_marker(self, map_or_cluster, property_data: Dict[str, Any]):
        """Ajoute un marker de propriété"""
        try:
            # Couleur selon le type
            prop_type = property_data.get('property_type', '').lower()
            color = self.marker_colors.get(prop_type, 'blue')
            
            # Icône selon le type
            icon_map = {
                'appartement': 'building',
                'maison': 'home',
                'villa': 'home',
                'studio': 'building',
                'penthouse': 'building'
            }
            icon = icon_map.get(prop_type, 'home')
            
            # Créer le popup
            popup_html = self._create_property_popup(property_data)
            
            # Marker
            folium.Marker(
                location=[property_data['latitude'], property_data['longitude']],
                popup=folium.Popup(popup_html, max_width=300),
                tooltip=f"{property_data['title']} - {property_data['price']:,}€",
                icon=folium.Icon(color=color, icon=icon, prefix='fa')
            ).add_to(map_or_cluster)
            
        except Exception as e:
            logger.error(f"Erreur ajout marker propriété: {e}")
    
    def _create_property_popup(self, property_data: Dict[str, Any]) -> str:
        """Crée le contenu du popup pour une propriété"""
        try:
            # Image
            images = property_data.get('images', [])
            img_html = ""
            if images:
                img_html = f'<img src="{images[0]}" style="width: 100%; max-width: 250px; height: 150px; object-fit: cover; border-radius: 8px; margin-bottom: 10px;">'
            
            # Caractéristiques
            characteristics = []
            if property_data.get('bedrooms'):
                characteristics.append(f"🛏️ {property_data['bedrooms']} ch.")
            if property_data.get('bathrooms'):
                characteristics.append(f"🚿 {property_data['bathrooms']} sdb")
            if property_data.get('surface'):
                characteristics.append(f"📐 {property_data['surface']}m²")
            
            char_html = " • ".join(characteristics) if characteristics else ""
            
            # Équipements
            features = property_data.get('features', [])[:3]  # Max 3
            features_html = ""
            if features:
                features_html = f"<div style='margin-top: 8px;'>✨ {' • '.join(features)}</div>"
            
            # Prix/m²
            price_per_m2 = ""
            if property_data.get('surface', 0) > 0:
                ppm2 = property_data['price'] / property_data['surface']
                price_per_m2 = f"<div style='font-size: 0.9em; color: #666;'>{ppm2:,.0f}€/m²</div>"
            
            popup_html = f"""
            <div style="font-family: Arial, sans-serif; max-width: 250px;">
                {img_html}
                <h4 style="margin: 0 0 8px 0; color: {COLORS['primary']};">
                    {property_data['title'][:40]}{'...' if len(property_data['title']) > 40 else ''}
                </h4>
                
                <div style="font-size: 1.2em; font-weight: bold; color: {COLORS['primary']}; margin-bottom: 8px;">
                    💰 {property_data['price']:,}€
                </div>
                {price_per_m2}
                
                <div style="margin: 8px 0; color: #555;">
                    🏠 {property_data['property_type']}
                </div>
                
                {f'<div style="margin: 8px 0; color: #555;">{char_html}</div>' if char_html else ''}
                
                <div style="margin: 8px 0; color: #666;">
                    📍 {property_data['location']}
                </div>
                
                {features_html}
                
                <div style="margin-top: 10px; padding-top: 8px; border-top: 1px solid #eee;">
                    <small style="color: #888;">
                        💬 {property_data.get('agent_contact', 'Contact via ImoMatch')}
                    </small>
                </div>
            </div>
            """
            
            return popup_html
            
        except Exception as e:
            logger.error(f"Erreur création popup: {e}")
            return f"<div><h4>{property_data.get('title', 'Propriété')}</h4><p>{property_data.get('price', 0):,}€</p></div>"
    
    def _create_comparison_popup(self, property_data: Dict[str, Any], number: int) -> str:
        """Crée un popup pour la comparaison"""
        popup_html = f"""
        <div style="font-family: Arial, sans-serif;">
            <h4 style="color: {COLORS['primary']};">Propriété #{number}</h4>
            <h5>{property_data['title'][:30]}...</h5>
            <p><strong>{property_data['price']:,}€</strong></p>
            <p>📐 {property_data.get('surface', 'N/A')}m² • 🏠 {property_data['property_type']}</p>
            <p>📍 {property_data['location']}</p>
        </div>
        """
        return popup_html
    
    def _add_comparison_legend(self, m: folium.Map, properties: List[Dict[str, Any]], 
                              colors: List[str]):
        """Ajoute une légende pour la comparaison"""
        try:
            legend_html = """
            <div style="position: fixed; 
                        top: 10px; right: 10px; width: 200px; height: auto; 
                        background-color: white; border:2px solid grey; z-index:9999; 
                        font-size:14px; padding: 10px">
                <p><strong>Comparaison des Propriétés</strong></p>
            """
            
            for i, (prop, color) in enumerate(zip(properties, colors)):
                legend_html += f"""
                <p><i class="fa fa-circle" style="color:{color}"></i> 
                   #{i+1} {prop['title'][:20]}{'...' if len(prop['title']) > 20 else ''}<br>
                   <small>{prop['price']:,}€</small>
                </p>
                """
            
            legend_html += "</div>"
            
            m.get_root().html.add_child(folium.Element(legend_html))
            
        except Exception as e:
            logger.error(f"Erreur ajout légende: {e}")
    
    def _add_map_controls(self, m: folium.Map):
        """Ajoute les contrôles à la carte"""
        try:
            # Plein écran
            plugins.Fullscreen().add_to(m)
            
            # Localisation
            plugins.LocateControl().add_to(m)
            
            # Mesure
            plugins.MeasureControl().add_to(m)
            
        except Exception as e:
            logger.error(f"Erreur ajout contrôles: {e}")
    
    def _calculate_center(self, properties: List[Dict[str, Any]]) -> Tuple[float, float]:
        """Calcule le centre géographique d'une liste de propriétés"""
        try:
            valid_coords = [
                (prop['latitude'], prop['longitude'])
                for prop in properties
                if prop.get('latitude') and prop.get('longitude')
            ]
            
            if not valid_coords:
                return self.default_location
            
            avg_lat = sum(coord[0] for coord in valid_coords) / len(valid_coords)
            avg_lng = sum(coord[1] for coord in valid_coords) / len(valid_coords)
            
            return (avg_lat, avg_lng)
            
        except Exception as e:
            logger.error(f"Erreur calcul centre: {e}")
            return self.default_location
    
    def _fit_bounds_to_properties(self, m: folium.Map, properties: List[Dict[str, Any]]):
        """Ajuste la vue pour inclure toutes les propriétés"""
        try:
            coords = [
                [prop['latitude'], prop['longitude']]
                for prop in properties
                if prop.get('latitude') and prop.get('longitude')
            ]
            
            if len(coords) > 1:
                m.fit_bounds(coords, padding=(20, 20))
                
        except Exception as e:
            logger.error(f"Erreur ajustement bounds: {e}")
    
    def _calculate_zoom_for_radius(self, radius_km: float) -> int:
        """Calcule le niveau de zoom approprié pour un rayon donné"""
        # Formule approximative
        zoom_levels = {
            50: 9,
            25: 10,
            10: 11,
            5: 12,
            2: 13,
            1: 14,
            0.5: 15
        }
        
        for max_radius, zoom in zoom_levels.items():
            if radius_km >= max_radius:
                return zoom
        
        return 16  # Zoom par défaut pour petits rayons
    
    def _create_fallback_map(self) -> folium.Map:
        """Crée une carte de fallback en cas d'erreur"""
        return folium.Map(
            location=self.default_location,
            zoom_start=self.default_zoom,
            tiles='OpenStreetMap'
        )


class MapStyler:
    """Gestionnaire des styles de cartes personnalisés"""
    
    @staticmethod
    def get_custom_marker_icon(property_type: str, price_range: str = 'medium') -> folium.Icon:
        """
        Retourne une icône personnalisée selon le type et prix
        
        Args:
            property_type: Type de propriété
            price_range: Gamme de prix ('low', 'medium', 'high', 'luxury')
            
        Returns:
            folium.Icon: Icône personnalisée
        """
        # Couleurs selon le prix
        price_colors = {
            'low': 'green',
            'medium': 'blue', 
            'high': 'orange',
            'luxury': 'red'
        }
        
        # Icônes selon le type
        type_icons = {
            'appartement': 'building',
            'maison': 'home',
            'villa': 'home',
            'studio': 'building',
            'penthouse': 'star'
        }
        
        color = price_colors.get(price_range, 'blue')
        icon = type_icons.get(property_type.lower(), 'home')
        
        return folium.Icon(color=color, icon=icon, prefix='fa')
    
    @staticmethod
    def apply_dark_theme(m: folium.Map) -> folium.Map:
        """Applique un thème sombre à la carte"""
        try:
            # Tuiles sombres
            folium.TileLayer(
                tiles='cartodbdark_matter',
                name='Dark Theme',
                overlay=False,
                control=True
            ).add_to(m)
            
            return m
        except Exception as e:
            logger.error(f"Erreur application thème sombre: {e}")
            return m


# Fonctions utilitaires
def create_simple_map(properties: List[Dict[str, Any]], **kwargs) -> folium.Map:
    """
    Fonction simple pour créer une carte avec propriétés
    
    Args:
        properties: Liste des propriétés
        **kwargs: Arguments additionnels
        
    Returns:
        folium.Map: Carte créée
    """
    manager = MapManager()
    return manager.create_properties_map(properties, **kwargs)

def get_map_bounds(properties: List[Dict[str, Any]]) -> Optional[List[List[float]]]:
    """
    Calcule les bounds pour une liste de propriétés
    
    Args:
        properties: Liste des propriétés
        
    Returns:
        List des bounds ou None
    """
    try:
        coords = [
            [prop['latitude'], prop['longitude']]
            for prop in properties
            if prop.get('latitude') and prop.get('longitude')
        ]
        
        if not coords:
            return None
        
        # Calculer min/max lat/lng
        lats = [coord[0] for coord in coords]
        lngs = [coord[1] for coord in coords]
        
        return [
            [min(lats), min(lngs)],  # Sud-Ouest
            [max(lats), max(lngs)]   # Nord-Est
        ]
        
    except Exception as e:
        logger.error(f"Erreur calcul bounds: {e}")
        return None

# Instance globale
map_manager = MapManager()

def get_map_manager() -> MapManager:
    """Retourne l'instance du gestionnaire de cartes"""
    return map_manager
                
