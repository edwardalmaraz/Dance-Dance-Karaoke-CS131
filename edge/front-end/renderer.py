import pygame


def render(state):
    window = state["window"]
    window.fill(state["BLACK"])

    if state["current_display"] == "start_screen":
        title_rect = state["title_text"].get_rect(center=(state["window_width"] // 2, 120))
        window.blit(state["title_text"], title_rect)

        play_rect = state["play_song_text"].get_rect(center=(state["window_width"] // 2, 300))
        library_rect = state["online_library_text"].get_rect(center=(state["window_width"] // 2, 370))
        leaderboard_rect = state["leaderboard_text"].get_rect(center=(state["window_width"] // 2, 440))

        window.blit(state["play_song_text"], play_rect)
        window.blit(state["online_library_text"], library_rect)
        window.blit(state["leaderboard_text"], leaderboard_rect)

    elif state["current_display"] == "gameplay":
        pygame.draw.rect(window, state["WHITE"], state["left_rect"], state["LINE_WIDTH"])
        pygame.draw.rect(window, state["WHITE"], state["right_rect"], state["LINE_WIDTH"])
        pygame.draw.rect(window, state["WHITE"], state["bottom_rect"], state["LINE_WIDTH"])

        text_surface1 = state["small_font"].render(state["The_Feels"].lyrics[state["current_lyrics_index"] - 1].text, True, state["WHITE"]) 
        text_surface2 = state["big_font"].render(state["The_Feels"].lyrics[state["current_lyrics_index"]].text, True, state["YELLOW"]) 

        text_rect1 = text_surface1.get_rect(center=(state["bottom_rect"].centerx, state["bottom_rect"].top + 80))
        text_rect2 = text_surface2.get_rect(center=state["bottom_rect"].center)

        window.blit(text_surface1, text_rect1)
        window.blit(text_surface2, text_rect2)

        if state["current_lyrics_index"] + 1 < len(state["The_Feels"].lyrics):
            text_surface3 = state["small_font"].render(state["The_Feels"].lyrics[state["current_lyrics_index"] + 1].text, True, state["WHITE"]) 
            text_rect3 = text_surface3.get_rect(center=(state["bottom_rect"].centerx, state["bottom_rect"].bottom - 80))
            window.blit(text_surface3, text_rect3)

        # left box reserved for pose model or other content (camera removed)

        window.blit(state["pose_images"][state["current_pose_index"]], state["right_rect"])

        pygame.draw.rect(window, state["BLACK"], state["button_rect"], state["LINE_WIDTH"])
        window.blit(state["button_text"], (state["button_rect"].x + 15, state["button_rect"].y + 15))

    elif state["current_display"] == "leaderboard":
        title_rect = state["leaderboard_title_text"].get_rect(center=(state["window_width"] // 2, 100))
        window.blit(state["leaderboard_title_text"], title_rect)

        entry_start_y = 200
        entry_spacing = 60

        for index, entry in enumerate(state["leaderboard_entries"]):
            entry_string = f"{entry.rank}.  {entry.player_name:<10}  {entry.score}"
            entry_surface = state["leaderboard_entry_font"].render(entry_string, True, state["WHITE"]) if "leaderboard_entry_font" in state else state["label_font"].render(entry_string, True, state["WHITE"]) 
            entry_rect = entry_surface.get_rect(center=(state["window_width"] // 2, entry_start_y + index * entry_spacing))
            window.blit(entry_surface, entry_rect)

        hint_rect = state["leaderboard_hint_text"].get_rect(center=(state["window_width"] // 2, state["window_height"] - 60))
        window.blit(state["leaderboard_hint_text"], hint_rect)

    elif state["current_display"] == "end_screen":
        song_name_rect = state["end_song_name_text"].get_rect(center=(state["window_width"] // 2, 150))
        window.blit(state["end_song_name_text"], song_name_rect)

        score_rect = state["end_score_text"].get_rect(center=(state["window_width"] // 2, state["window_height"] // 2))
        window.blit(state["end_score_text"], score_rect)

        hint_rect = state["end_hint_text"].get_rect(center=(state["window_width"] // 2, state["window_height"] - 80))
        window.blit(state["end_hint_text"], hint_rect)

    pygame.display.flip()
