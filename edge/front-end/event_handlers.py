import pygame


def handle_events(state):
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            state["run"] = False

        if e.type == pygame.MOUSEBUTTONDOWN:
            if state["current_display"] == "start_screen":
                pass

            elif state["current_display"] == "gameplay":
                if state["button_rect"].collidepoint(e.pos):
                    if state["game_state"] == "not_started":
                        pygame.mixer.music.play()
                        state["song_start_time"] = pygame.time.get_ticks()
                        state["game_state"] = "playing"
                        state["button_text"] = state["button_font"].render("PAUSE", True, state["BLACK"]) 

                    elif state["game_state"] == "playing":
                        pygame.mixer.music.pause()
                        state["pause_start_time"] = pygame.time.get_ticks()
                        state["game_state"] = "paused"
                        state["button_text"] = state["button_font"].render("PLAY", True, state["BLACK"]) 

                    elif state["game_state"] == "paused":
                        pygame.mixer.music.unpause()
                        paused_duration = pygame.time.get_ticks() - state.get("pause_start_time", 0)
                        state["song_start_time"] += paused_duration
                        state["game_state"] = "playing"
                        state["button_text"] = state["button_font"].render("PAUSE", True, state["BLACK"]) 

            elif state["current_display"] == "leaderboard":
                pass

        if e.type == pygame.KEYDOWN:
            if state["current_display"] == "start_screen":
                if e.key == pygame.K_1:
                    state["current_display"] = "gameplay"
                elif e.key == pygame.K_2:
                    print("online library - not built yet")
                elif e.key == pygame.K_3:
                    state["current_display"] = "leaderboard"

            elif state["current_display"] == "gameplay":
                if e.key == pygame.K_ESCAPE:
                    if state["game_state"] == "paused" or state["game_state"] == "not_started":
                        pygame.mixer.music.stop()
                        state["game_state"] = "not_started"
                        state["current_lyrics_index"] = 1
                        state["current_pose_index"] = 0
                        state["button_text"] = state["button_font"].render("START", True, state["BLACK"]) 
                        state["current_display"] = "start_screen"

            elif state["current_display"] == "leaderboard":
                if e.key == pygame.K_ESCAPE or e.key == pygame.K_DELETE:
                    state["current_display"] = "start_screen"

            elif state["current_display"] == "end_screen":
                if e.key == pygame.K_RETURN:
                    state["current_display"] = "start_screen"


def update_state(state):
    # advance lyric/pose indices while playing
    if state.get("game_state") == "playing":
        current_song_time = pygame.time.get_ticks() - state.get("song_start_time", 0)

        if state["current_lyrics_index"] + 1 < len(state["The_Feels"].lyrics):
            if current_song_time >= state["The_Feels"].lyrics[state["current_lyrics_index"] + 1].timestamp_ms:
                state["current_lyrics_index"] += 1

        if state["current_pose_index"] + 1 < len(state["The_Feels"].poses):
            if current_song_time >= state["The_Feels"].poses[state["current_pose_index"] + 1].timestamp_ms:
                state["current_pose_index"] += 1

    # detect natural song end
    if state.get("game_state") == "playing" and not pygame.mixer.music.get_busy():
        state["game_state"] = "not_started"
        state["current_lyrics_index"] = 1
        state["current_pose_index"] = 0
        state["current_display"] = "end_screen"
        state["button_text"] = state["button_font"].render("START", True, state["BLACK"]) 
