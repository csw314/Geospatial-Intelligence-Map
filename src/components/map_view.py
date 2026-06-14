"""Dash Leaflet map component."""

from __future__ import annotations

from typing import Any

import dash_leaflet as dl
from dash_extensions.javascript import assign

from src.config import INITIAL_CENTER, INITIAL_ZOOM, AppSettings
from src.data.schemas import LocationRecord
from src.utils.marker_styles import records_to_geojson

POINT_TO_LAYER = assign(
    """
function(feature, latlng) {
    const p = feature.properties || {};
    const escapeHtml = (value) => String(value ?? "").replace(/[&<>"']/g, function(ch) {
        return {"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"}[ch];
    });
    const selected = Boolean(p.selected);
    const isMetro = p.map_layer === "global_metros";
    const isUs = p.map_layer === "us_military";
    const size = selected ? (isMetro ? 40 : isUs ? 39 : 38) : (isMetro ? 32 : isUs ? 33 : 31);
    const markerBaseClass = isMetro ? "metro-marker" : isUs ? "us-marker" : "location-marker";
    const markerClass = `${markerBaseClass}${selected ? " is-selected" : ""}`;
    const html = `
        <div class="${markerClass}"
             style="--marker-color:${p.marker_color};--type-color:${p.type_color};">
            <span>${escapeHtml(p.type_code || "?")}</span>
        </div>`;
    const marker = L.marker(latlng, {
        icon: L.divIcon({
            html: html,
            className: "location-marker-shell",
            iconSize: [size, size],
            iconAnchor: [size / 2, size / 2],
            popupAnchor: [0, -size / 2]
        }),
        keyboard: true,
        title: p.name
    });
    const tooltip = `<strong>${escapeHtml(p.name)}</strong><br>` +
        `${escapeHtml(p.country)} | ${escapeHtml(p.type)}`;
    marker.bindTooltip(tooltip, {direction: "top", offset: [0, -12], opacity: 0.95});
    marker.bindPopup(
        `<div class="marker-popup"><strong>${escapeHtml(p.name)}</strong><br>` +
        `${escapeHtml(p.country)} | ${escapeHtml(p.type)}<br>` +
        `Select marker for full details.</div>`
    );
    return marker;
}
"""
)

CLUSTER_TO_LAYER = assign(
    """
function(feature, latlng) {
    const count = feature.properties.point_count;
    const size = count < 10 ? 34 : count < 100 ? 42 : 50;
    const html = `<div class="cluster-marker"><span>${count}</span></div>`;
    return L.marker(latlng, {
        icon: L.divIcon({
            html: html,
            className: "cluster-marker-shell",
            iconSize: [size, size],
            iconAnchor: [size / 2, size / 2]
        })
    });
}
"""
)


def build_map(records: list[LocationRecord], settings: AppSettings) -> Any:
    """Build the Leaflet map."""

    locations_layer = dl.GeoJSON(
        id="locations-layer",
        data=records_to_geojson(records),
        cluster=True,
        zoomToBoundsOnClick=True,
        superClusterOptions={"radius": 48, "maxZoom": 8},
        pointToLayer=POINT_TO_LAYER,
        clusterToLayer=CLUSTER_TO_LAYER,
    )

    return dl.Map(
        id="map",
        center=INITIAL_CENTER,
        zoom=INITIAL_ZOOM,
        minZoom=2,
        zoomControl=True,
        worldCopyJump=True,
        preferCanvas=False,
        className="map",
        children=[
            dl.LayersControl(
                [
                    dl.BaseLayer(
                        dl.TileLayer(
                            url=settings.tile_url,
                            attribution=settings.tile_attribution,
                            maxZoom=20,
                        ),
                        name=settings.tile_layer_name,
                        checked=True,
                    ),
                    dl.Overlay(locations_layer, name="Locations", checked=True),
                ],
                position="topright",
            ),
            dl.ScaleControl(position="bottomleft"),
            dl.FullScreenControl(position="topright"),
        ],
    )
