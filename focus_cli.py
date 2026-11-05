#!/usr/bin/env python3
"""
Focus Saver - Terminal CLI Version
Terminal üzerinden odaklanma seansını başlatır.
"""

import argparse
import os
import sys

# Proje dizinini sys.path'e ekle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import time
from core.session_manager import FocusSessionManager

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn
    from rich.table import Table
    HAS_RICH = True
except ImportError:
    HAS_RICH = False


def run_cli(minutes):
    mgr = FocusSessionManager()
    console = Console() if HAS_RICH else None

    if HAS_RICH:
        table = Table(show_header=False, box=None)
        table.add_row("⏱️ Süre:", f"[bold cyan]{minutes} Dakika[/bold cyan]")
        table.add_row("🚫 Engelliler:", "[bold red]YouTube, Kick, Twitch, Instagram, Arama Sorguları[/bold red]")
        table.add_row("🎵 İzin Verilen:", "[bold green]YouTube Music (music.youtube.com)[/bold green]")
        table.add_row("🌐 Kapsam:", "[bold yellow]Safari & Google Chrome & Tüm macOS[/bold yellow]")

        console.print(Panel(table, title="[bold white]🎯 Focus Saver (Odak Koruyucu)[/bold white]", border_style="blue"))
        console.print("[dim]Durdurmak için Ctrl+C tuşlarına basabilirsiniz.[/dim]\n")
    else:
        print(f"🎯 Focus Saver Başlatılıyor: {minutes} dakika...")
        print("Engelli: YouTube, Kick, Twitch, Instagram | İzin: YouTube Music")
        print("Durdurmak için Ctrl+C tuşlarına basın.\n")

    mgr.start(minutes)
    total_seconds = minutes * 60

    try:
        if HAS_RICH:
            with Progress(
                TextColumn("[progress.description]{task.description}"),
                BarColumn(complete_style="red", finished_style="green"),
                TextColumn("[bold yellow]{task.fields[remaining]}[/bold yellow]"),
                TimeRemainingColumn(),
                console=console
            ) as progress:
                task = progress.add_task("[bold red]Odaklanma Seansı", total=total_seconds, remaining=mgr.get_formatted_time())

                while mgr.is_running:
                    rem = mgr.get_remaining_seconds()
                    if rem <= 0:
                        break
                    progress.update(task, completed=(total_seconds - rem), remaining=mgr.get_formatted_time())
                    time.sleep(0.5)
        else:
            while mgr.is_running:
                rem = mgr.get_remaining_seconds()
                if rem <= 0:
                    break
                print(f"\r⏳ Kalan Süre: {mgr.get_formatted_time()} ", end="", flush=True)
                time.sleep(1)
            print()

        print("\n🎉 Tebrikler! Odaklanma süreniz tamamlandı. Korumalar kaldırıldı.")
    except KeyboardInterrupt:
        print("\n\n⏹️ Kullanıcı isteğiyle durduruldu. Korumalar kaldırılıyor...")
        mgr.stop()
        print("✅ Korumalar kaldırıldı, sistem normale döndü.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Focus Saver CLI")
    parser.add_argument("minutes", type=int, nargs="?", default=25, help="Odaklanma süresi (dakika, varsayılan: 25)")
    args = parser.parse_args()

    run_cli(args.minutes)
