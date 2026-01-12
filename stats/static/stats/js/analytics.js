async function loadAnalytics() {
    const params = new URLSearchParams();

    document.querySelectorAll("#players option:checked")
        .forEach(o => params.append("players[]", o.value));

    document.querySelectorAll("#matches option:checked")
        .forEach(o => params.append("matches[]", o.value));

    document.querySelectorAll("#seasons option:checked")
        .forEach(o => params.append("seasons[]", o.value));

    document.querySelectorAll("#event_types option:checked")
        .forEach(o => params.append("event_types[]", o.value));

    const res = await fetch(`/stats/analytics/data/?${params.toString()}`);
    const data = await res.json();

    console.log("Analytics data:", data);
    // Chart logic comes next
}

document.querySelectorAll("select").forEach(sel => {
    sel.addEventListener("change", loadAnalytics);
});
