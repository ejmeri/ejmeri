#!/usr/bin/env python3
"""Generate an animated terminal-window SVG for the GitHub profile header.

Commands are "typed" character by character (SMIL clip-path animation), each
output line fades in after its command, and the final prompt has a blinking
cursor. No scripts, so it animates inside GitHub's <img> rendering.

Usage: python3 scripts/make_terminal.py profile/terminal.svg
"""
import sys
from xml.sax.saxutils import escape

W, PAD_X, TOP, LINE_H, FONT = 860, 24, 64, 24, 15
CHAR_W = FONT * 0.62          # generous monospace advance so steps never cut a glyph
TYPE_MS, OUT_DELAY, NEXT_DELAY = 45, 250, 450

PROMPT = [("elmeri", "#3fb950"), ("@", "#8b949e"), ("dev", "#3fb950"), (" ~ ", "#58a6ff"), ("$ ", "#e6edf3")]
SESSION = [
    ("whoami", [[("Elmeri Moreno", "#d2a8ff"), (" — ", "#8b949e"), ("Senior Software Engineer @ XP Inc", "#e6edf3")]]),
    ("cat focus.txt", [[("backend systems", "#79c0ff"), (" · ", "#8b949e"), ("apis", "#79c0ff"),
                        (" · ", "#8b949e"), ("event-driven architecture", "#79c0ff")]]),
    ("echo $STACK", [[("java c# typescript", "#ffa657"), ("  |  ", "#8b949e"), ("kafka rabbitmq sqs", "#ff7b72"),
                      ("  |  ", "#8b949e"), ("postgres sqlserver redis", "#7ee787")]]),
    ("cat azure-pipelines.yml | grep stage", [[("build", "#7ee787"), (" → ", "#8b949e"), ("test", "#7ee787"), (" → ", "#8b949e"),
                                               ("deploy", "#7ee787"), ("  ·  ", "#8b949e"), ("docker · kubernetes · azure · aws", "#79c0ff")]]),
    ("uptime", [[("coding since 2015", "#e6edf3"), (" · ", "#8b949e"), ("10+ years", "#f2cc60"),
                 (" · ", "#8b949e"), ("São Paulo, BR", "#e6edf3")]]),
]
PROMPT_LEN = sum(len(t) for t, _ in PROMPT)


def tspans(parts):
    return "".join(f'<tspan fill="{c}">{escape(t)}</tspan>' for t, c in parts)


def main(out):
    rows, defs = [], []
    y, t = TOP, 600  # ms
    for i, (cmd, outputs) in enumerate(SESSION):
        # prompt appears, then the command is typed via a stepped clip rect
        x_cmd = PAD_X + PROMPT_LEN * CHAR_W
        steps = ";".join(str(round(k * CHAR_W, 1)) for k in range(len(cmd) + 1))
        dur = TYPE_MS * len(cmd)
        defs.append(
            f'<clipPath id="c{i}"><rect x="{x_cmd:.1f}" y="{y - 18}" height="{LINE_H}" width="0">'
            f'<animate attributeName="width" values="{steps}" calcMode="discrete" '
            f'begin="{t}ms" dur="{dur}ms" fill="freeze"/></rect></clipPath>'
        )
        rows.append(
            f'<g opacity="0"><set attributeName="opacity" to="1" begin="{t}ms" fill="freeze"/>'
            f'<text x="{PAD_X}" y="{y}">{tspans(PROMPT)}</text>'
            f'<text x="{x_cmd:.1f}" y="{y}" fill="#e6edf3" clip-path="url(#c{i})">{escape(cmd)}</text></g>'
        )
        t += dur + OUT_DELAY
        for parts in outputs:
            y += LINE_H
            rows.append(
                f'<text x="{PAD_X}" y="{y}" opacity="0">{tspans(parts)}'
                f'<animate attributeName="opacity" from="0" to="1" begin="{t}ms" dur="300ms" fill="freeze"/></text>'
            )
        y += LINE_H + 6
        t += NEXT_DELAY

    # final prompt with blinking cursor
    x_cur = PAD_X + PROMPT_LEN * CHAR_W
    rows.append(
        f'<g opacity="0"><set attributeName="opacity" to="1" begin="{t}ms" fill="freeze"/>'
        f'<text x="{PAD_X}" y="{y}">{tspans(PROMPT)}</text>'
        f'<rect x="{x_cur:.1f}" y="{y - 14}" width="9" height="18" fill="#3fb950">'
        f'<animate attributeName="opacity" values="1;0;1" dur="1s" begin="{t}ms" repeatCount="indefinite"/></rect></g>'
    )
    H = y + 26

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Elmeri Moreno — Senior Software Engineer @ XP Inc">
<defs>{"".join(defs)}</defs>
<style>text {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, "Liberation Mono", monospace; font-size: {FONT}px; white-space: pre; }}</style>
<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="10" fill="#0d1117" stroke="#30363d"/>
<path d="M0.5 10.5 a10 10 0 0 1 10 -10 h{W - 21} a10 10 0 0 1 10 10 v25.5 h-{W - 1} z" fill="#161b22"/>
<line x1="0.5" y1="36" x2="{W - 0.5}" y2="36" stroke="#30363d"/>
<circle cx="22" cy="18" r="6" fill="#ff5f57"/><circle cx="42" cy="18" r="6" fill="#febc2e"/><circle cx="62" cy="18" r="6" fill="#28c840"/>
<text x="{W / 2}" y="23" text-anchor="middle" fill="#8b949e" style="font-size:13px">elmeri@dev: ~ — zsh</text>
{chr(10).join(rows)}
</svg>
'''
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(svg)


if __name__ == "__main__":
    main(sys.argv[1])
