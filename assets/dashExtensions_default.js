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
                const isMetro = p.dataset_type === "metro_area";
                const size = selected ? (isMetro ? 40 : 38) : (isMetro ? 32 : 31);
                const markerClass = `${isMetro ? "metro-marker" : "location-marker"}` +
                    `${selected ? " is-selected" : ""}`;
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
                marker.bindPopup(p.popup_html || "");
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