window.dashExtensions = Object.assign({}, window.dashExtensions, {
    default: {
        function0: function(feature, latlng) {
                const p = feature.properties || {};
                const escapeHtml = (value) => String(value ?? "").replace(/[&<>"']/g, function(ch) {
                    return {
                        "&": "&amp;",
                        "<": "&lt;",
                        ">": "&gt;",
                        '"': "&quot;",
                        "'": "&#39;"
                    } [ch];
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
                marker.bindTooltip(tooltip, {
                    direction: "top",
                    offset: [0, -12],
                    opacity: 0.95
                });
                marker.bindPopup(
                    `<div class="marker-popup"><strong>${escapeHtml(p.name)}</strong><br>` +
                    `${escapeHtml(p.country)} | ${escapeHtml(p.type)}<br>` +
                    `Select marker for full details.</div>`
                );
                return marker;
            }

            ,
        function1: function(feature, latlng) {
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

    }
});