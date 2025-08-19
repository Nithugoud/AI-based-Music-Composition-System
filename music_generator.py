import pretty_midi

def generate_music(params, filename="output.mid"):
    # Create a PrettyMIDI object
    midi = pretty_midi.PrettyMIDI()
    instrument = pretty_midi.Instrument(program=40)  # Violin default (program 40)

    # Map scale (simple C major notes)
    scale_notes = [60, 62, 64, 65, 67, 69, 71, 72]  # C major

    tempo = params.get("tempo", 120)
    energy = params.get("energy", 0.5)
    duration = 0.5 if energy < 0.5 else 1.0

    # Generate a simple melody
    time = 0
    for i in range(16):
        pitch = scale_notes[i % len(scale_notes)]
        note = pretty_midi.Note(
            velocity=100,
            pitch=pitch,
            start=time,
            end=time + duration
        )
        instrument.notes.append(note)
        time += duration

    midi.instruments.append(instrument)
    midi.write(filename)
    print(f"✅ Music saved as {filename}")

# Example usage
params = {"tempo": 139, "scale": "C major", "instrument": "violin", "energy": 0.8}
generate_music(params, "test_output.mid")
