import os
import shutil
import pygame
from record import start_recording, pause_recording, resume_recording, stop_recording
from comparsion_pose import parse_pose_sequence_data, parse_frame_data, compare_sequence_to_frames, total_accuracy
from draw_pose import draw_pose, draw_all_poses
from cloud_api import submit_final_score, fetch_leaderboard, fetch_songs, download_song
from UI.models import LeaderboardEntry, Song


# path where pose keypoints are appended every POSE_SNAPSHOT_INTERVAL_MS
POSE_OUTPUT_FILE = "player_poses/pose_locations.txt"
os.makedirs(os.path.dirname(POSE_OUTPUT_FILE), exist_ok=True)

# song metadata needed by the pose comparison score
POSE_COMPARISON_FILE = "songs/metadata.json"
os.makedirs(os.path.dirname(POSE_COMPARISON_FILE), exist_ok=True)
POSE_SNAPSHOT_INTERVAL_MS = 5000


def _write_pose_snapshot(state, current_song_time_ms):
    """Append all currently detected pose keypoints (as neck-relative direction
    vectors) to POSE_OUTPUT_FILE.  Called every POSE_SNAPSHOT_INTERVAL_MS while
    the game is in the "playing" state."""
    poses = state.get("poses", [])
    camera = state.get("pose_camera")
    elapsed = current_song_time_ms / 1000.0

    with open(POSE_OUTPUT_FILE, "a") as f:
        f.write(f"\n=== Timestamp: {elapsed:.1f}s ===\n")
        if not poses:
            f.write("  No poses detected\n")
            return
        for pose in poses:
            # find the neck keypoint to use as the reference origin
            neck_kp = None
            for kp in pose.Keypoints:
                if camera.available and camera.net.GetKeypointName(kp.ID) == "neck":
                    neck_kp = kp
                    break
            if neck_kp is not None:
                f.write("    Direction Vectors (relative to neck):\n")
                for kp in pose.Keypoints:
                    name = camera.net.GetKeypointName(kp.ID)
                    if name == "neck":
                        continue
                    vec_x = neck_kp.x - kp.x
                    vec_y = neck_kp.y - kp.y
                    f.write(f"      neck -> {name}: ({vec_x:.1f}, {vec_y:.1f})\n")
            else:
                f.write("    Neck not detected, skipping direction vectors\n")


# ---------------------------------------------------------------------------
# Event handler — called once per frame from the main loop
# ---------------------------------------------------------------------------

def handle_events(state):
    """Process all pending pygame events and update state accordingly.

    The function is a big dispatch on state["current_display"] so each screen
    only reacts to events that are relevant to it.
    """
    for e in pygame.event.get():

        # window close button 
        if e.type == pygame.QUIT:
            state["run"] = False

        # mouse clicks 
        if e.type == pygame.MOUSEBUTTONDOWN:
            if state["current_display"] == "start_screen":
                pass  # start screen has no clickable elements yet

            elif state["current_display"] == "gameplay":
                # the START/PAUSE/PLAY button lives in button_rect
                if state["button_rect"].collidepoint(e.pos):
                    if state["game_state"] == "not_started":
                        # start the song, recording, and pose snapshot timer
                        state["song_start_time"] = pygame.time.get_ticks()
                        state["pose_last_snapshot_song_time_ms"] = 0
                        state["game_state"] = "playing"
                        state["button_text"] = state["button_font"].render("PAUSE", True, state["WHITE"])
                        if state["music_loaded"]:
                            pygame.mixer.music.play()
                        start_recording()

                    elif state["game_state"] == "playing":
                        # pause everything and remember when the pause started so
                        # we can offset song_start_time on resume
                        state["pause_start_time"] = pygame.time.get_ticks()
                        state["game_state"] = "paused"
                        state["button_text"] = state["button_font"].render("PLAY", True, state["WHITE"])
                        if state["music_loaded"]:
                            pygame.mixer.music.pause()
                        pause_recording()

                    elif state["game_state"] == "paused":
                        # shift song_start_time forward by the paused duration so
                        # all time calculations remain consistent
                        paused_duration = pygame.time.get_ticks() - state.get("pause_start_time", 0)
                        state["song_start_time"] += paused_duration
                        state["game_state"] = "playing"
                        state["button_text"] = state["button_font"].render("PAUSE", True, state["WHITE"])
                        if state["music_loaded"]:
                            pygame.mixer.music.unpause()
                        resume_recording()

            elif state["current_display"] == "leaderboard":
                pass  
        if e.type == pygame.KEYDOWN:

            # start screen: 1 = play, 2 = library, 3 = leaderboard 
            if state["current_display"] == "start_screen":
                if e.key == pygame.K_1:
                    # go to name entry before starting gameplay
                    state["player_name_input"] = ""
                    state["current_display"] = "name_entry"

                elif e.key == pygame.K_2:
                    # fetch available songs from the server and open the library
                    state["library_songs"] = fetch_songs()
                    state["library_selected_index"] = 0
                    state["current_display"] = "song_library"

                elif e.key == pygame.K_3:
                    # fetch available songs so the user can pick which song's leaderboard they want to view
                    state["leaderboard_songs"] = fetch_songs()
                    state["leaderboard_song_select_index"] = 0
                    state["current_display"] = "leaderboard_song_select"

            # name entry: type a name, ENTER confirms, ESC cancels 
            elif state["current_display"] == "name_entry":
                if e.key == pygame.K_ESCAPE:
                    state["current_display"] = "start_screen"
                elif e.key == pygame.K_BACKSPACE:
                    state["player_name_input"] = state["player_name_input"][:-1]
                elif e.key == pygame.K_RETURN:
                    name = state["player_name_input"].strip()
                    if name:
                        state["player_id"] = name
                        state["player_name_input"] = ""
                        state["current_display"] = "gameplay"
                        # clear the pose output file for a fresh recording
                        with open(POSE_OUTPUT_FILE, "w") as f:
                            f.write("")
                        # pre-render stick-figure images for every pose in the song
                        draw_all_poses("songs/metadata.json", save_individual=True, output_dir="poses")
                        right_rect = state["right_rect"]
                        state["pose_images"] = []
                        for pose_move in state["LOADED_SONG"].poses:
                            image = pygame.image.load(pose_move.image_path)
                            image = pygame.transform.scale(image, (int(right_rect.width * 0.7), int(right_rect.height * 0.7)))
                            state["pose_images"].append(image)
                elif e.unicode.isprintable() and len(state["player_name_input"]) < 20:
                    state["player_name_input"] += e.unicode

            # gameplay: ESC exits only when paused or not yet started
            elif state["current_display"] == "gameplay":
                if e.key == pygame.K_ESCAPE:
                    if state["game_state"] == "paused" or state["game_state"] == "not_started":
                        state["game_state"] = "not_started"
                        state["current_lyrics_index"] = 1
                        state["current_pose_index"] = 0
                        state["button_text"] = state["button_font"].render("START", True, state["WHITE"])
                        if state["music_loaded"]:
                            pygame.mixer.music.stop()
                        stop_recording()
                        state["current_display"] = "start_screen"

            # online library: browse and download songs 
            elif state["current_display"] == "song_library":
                songs = state["library_songs"]
                if e.key == pygame.K_ESCAPE:
                    state["current_display"] = "start_screen"
                elif e.key == pygame.K_UP and songs:
                    state["library_selected_index"] = (state["library_selected_index"] - 1) % len(songs)
                elif e.key == pygame.K_DOWN and songs:
                    state["library_selected_index"] = (state["library_selected_index"] + 1) % len(songs)
                elif e.key == pygame.K_RETURN and songs:
                    selected = songs[state["library_selected_index"]]
                    song_id = selected["song_id"]
                    print(f"Downloading song: {selected['song_title']} (id: {song_id})")
                    if download_song(song_id):
                        # reload everything that depends on the song metadata
                        state["LOADED_SONG"] = Song.from_json("songs/metadata.json")
                        state["song_duration_ms"] = max(
                            state["LOADED_SONG"].lyrics[-1].timestamp_ms if state["LOADED_SONG"].lyrics else 0,
                            state["LOADED_SONG"].poses[-1].timestamp_ms if state["LOADED_SONG"].poses else 0,
                        )
                        state["end_song_name_text"] = state["end_title_font"].render(state["LOADED_SONG"].song_title, True, state["WHITE"])
                        if pygame.mixer.get_init():
                            if state["music_loaded"]:
                                pygame.mixer.music.stop()
                            try:
                                pygame.mixer.music.load("songs/audio.mp3")
                                state["music_loaded"] = True
                            except pygame.error as ex:
                                state["music_loaded"] = False
                                print(f"Music load failed: {ex}")
                        state["current_display"] = "song_confirmed"
                    else:
                        print(f"Failed to download song {song_id}")

            # song confirmed: any key returns to start screen
            elif state["current_display"] == "song_confirmed":
                state["current_display"] = "start_screen"

            # leaderboard song select: pick a song to view scores for
            elif state["current_display"] == "leaderboard_song_select":
                songs = state.get("leaderboard_songs", [])
                if e.key == pygame.K_ESCAPE:
                    state["current_display"] = "start_screen"
                elif e.key == pygame.K_UP and songs:
                    state["leaderboard_song_select_index"] = (state["leaderboard_song_select_index"] - 1) % len(songs)
                elif e.key == pygame.K_DOWN and songs:
                    state["leaderboard_song_select_index"] = (state["leaderboard_song_select_index"] + 1) % len(songs)
                elif e.key == pygame.K_RETURN and songs:
                    selected = songs[state["leaderboard_song_select_index"]]
                    song_id = selected["song_id"]
                    # fetch ranked entries from the cloud for this song
                    # scores come back as a 0-100 float (e.g. 51.25 means 51.25%)
                    entries = fetch_leaderboard(song_id)
                    state["leaderboard_entries"] = [
                        LeaderboardEntry(player_name=entry["player_id"], score=round(entry["score"]), rank=i + 1)
                        for i, entry in enumerate(entries)
                    ]
                    # update the leaderboard title to show the selected song name
                    state["leaderboard_title_text"] = state["leaderboard_title_font"].render(
                        selected["song_title"].upper(), True, state["WHITE"]
                    )
                    state["current_display"] = "leaderboard"

            #  leaderboard: ESC goes back to song selection 
            elif state["current_display"] == "leaderboard":
                if e.key == pygame.K_ESCAPE or e.key == pygame.K_DELETE:
                    state["current_display"] = "leaderboard_song_select"

            #  end screen: ENTER returns to main menu 
            elif state["current_display"] == "end_screen":
                if e.key == pygame.K_RETURN:
                    state["current_display"] = "start_screen"

def update_state(state):
<<<<<<< Updated upstream
   # advance lyric/pose indices while playing
   if state.get("game_state") == "playing":
       current_song_time = pygame.time.get_ticks() - state.get("song_start_time", 0)


       if state["current_lyrics_index"] + 1 < len(state["LOADED_SONG"].lyrics):
           if current_song_time >= state["LOADED_SONG"].lyrics[state["current_lyrics_index"] + 1].timestamp_ms:
               state["current_lyrics_index"] += 1


       if state["current_pose_index"] + 1 < len(state["LOADED_SONG"].poses):
           if current_song_time >= state["LOADED_SONG"].poses[state["current_pose_index"] + 1].timestamp_ms:
               state["current_pose_index"] += 1


       last = state.get("pose_last_snapshot_song_time_ms", 0)
       if current_song_time - last >= POSE_SNAPSHOT_INTERVAL_MS:
           _write_pose_snapshot(state, current_song_time)
           state["pose_last_snapshot_song_time_ms"] = current_song_time


   # detect natural song end
   song_finished = False
   if state.get("game_state") == "playing":
       current_song_time = pygame.time.get_ticks() - state.get("song_start_time", 0)
       song_finished = current_song_time >= state.get("song_duration_ms", 0)


   if song_finished:
       state["game_state"] = "not_started"
       state["current_lyrics_index"] = 1
       state["current_pose_index"] = 0
       state["current_display"] = "end_screen"
       state["button_text"] = state["button_font"].render("START", True, state["BLACK"])
       if state["music_loaded"]:
           pygame.mixer.music.stop()
       stop_recording()


       #after song ends, calculate score based on pose comparison
       try:
           sequence_order, poses = parse_pose_sequence_data(POSE_COMPARISON_FILE)
           frame_data = parse_frame_data(POSE_OUTPUT_FILE)
           results = compare_sequence_to_frames(sequence_order, poses, frame_data)
           score = float(total_accuracy(results))
       except Exception as e:
           print(f"Score calculation failed: {e}")
           score = 0


       #should delete everything in the poses folder and recreate it so that the next time the game is played
       shutil.rmtree("poses", ignore_errors=True)
       os.makedirs("poses", exist_ok=True)


       song_id = state["LOADED_SONG"].song_id
       player_id = state.get("player_id", "player1")
       cloud_score = submit_final_score(
           song_id=song_id,
           player_id=player_id,
           wav_path="voice_recording/output.wav",
           move_score=score,
       )
       display_score = round(cloud_score * 100) if cloud_score is not None else score

       state["final_score"] = display_score
       state["end_score_text"] = state["end_score_font"].render(f"Score: {display_score}%", True, state["YELLOW"])


   if state["pose_camera"].available and not state["pose_camera"].is_streaming():
       state["run"] = False
