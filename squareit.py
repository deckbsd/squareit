import argparse
import wave

MIN = 1
MID = 2
MAX = 3
BYTES = 0

WAV_PCM_FORMATS = {'8': [1, 0, 128, 255], '16': [2, -32268, 0, 32767], '32': [4, -2147483648, 0, 2147483647]}


def signal_analyze(wav_input_file, bits, channels):
    peak_list = [[] for declare in range(channels)]
    last_frame_value = [None] * channels
    current_frame_value = [0] * channels
    sign = [False] * channels
    last_position_from_middle = [None] * channels
    current_position_from_middle = [True] * channels
    total_frames = wav_input_file.getnframes()
    for i in range(total_frames):
        frame = wav_input_file.readframes(1)
        for channel in range(0, channels):
            index = channel * 2
            frame_part = frame[index:index + WAV_PCM_FORMATS[bits][BYTES]]
            current_frame_value[channel] = int.from_bytes(frame_part, byteorder='little', signed=True)

            if current_frame_value[channel] >= WAV_PCM_FORMATS[bits][MID]:
                # High
                current_position_from_middle[channel] = True
            else:
                # Low
                current_position_from_middle[channel] = False

            if last_position_from_middle[channel] is None:
                last_position_from_middle[channel] = current_position_from_middle[channel]

            if current_position_from_middle[channel] != last_position_from_middle[channel] or i == (total_frames-1):
                (peak_list[channel]).append(last_frame_value[channel])
                last_frame_value[channel] = None
                last_position_from_middle[channel] = current_position_from_middle[channel]

            if current_frame_value[channel] >= 0:
                # +
                sign[channel] = True
            else:
                # -
                sign[channel] = False

            if sign[channel]:
                if last_frame_value[channel] is None or current_frame_value[channel] > last_frame_value[channel]:
                    last_frame_value[channel] = current_frame_value[channel]
            else:
                if last_frame_value[channel] is None or current_frame_value[channel] < last_frame_value[channel]:
                    last_frame_value[channel] = current_frame_value[channel]

    wav_input_file.rewind()
    return peak_list


if __name__ == "__main__":
    try:

        parser = argparse.ArgumentParser(description='transform sinusoidal signal to square.')
        parser.add_argument('--input', '-i', dest='input_file', required=True,
                            help='the wave file containing the input data. (required)')
        parser.add_argument('--output', '-o', dest='output_file', required=True,
                            help='the file where to put the transformation result. (required)')
        parser.add_argument('--bits', '-b', dest='bits', required=True,
                            help='The number of bits per sample')
        parser.add_argument('--amplification', '-a', dest='amp', default=False,
                            help='Do an amplification of the signal. (no by default)')
        args = parser.parse_args()

        input_file = args.input_file
        output_file = args.output_file
        selected_bits = args.bits
        to_amp = args.amp
        w = wave.open(input_file, 'r')
        wt = wave.open(output_file, "w")
        print("Copy parameters ...")

        output_params = w.getparams()
        channels = output_params.nchannels

        wt.setparams(output_params)
        if not to_amp:
            print("Analyzing signal...")
            peaks = signal_analyze(w, selected_bits, channels)
            print("Analyze finished [%d channels detected]" % channels)
            print("Copy and convert the signal...")
            peak_index = [0] * channels
            val_cmp = [0] * channels
            last_position_from_middle = [None] * channels
            current_position_from_middle = [True] * channels
            for i in range(w.getnframes()):
                frame = w.readframes(1)
                new_frame = bytearray()

                for channel in range(0, channels):
                    index = channel * 2
                    frame_cmp = frame[index:index + WAV_PCM_FORMATS[selected_bits][BYTES]]
                    frame_tmp = bytearray()
                    val_cmp[channel] = int.from_bytes(frame_cmp, byteorder='little', signed=True)

                    if val_cmp[channel] >= WAV_PCM_FORMATS[selected_bits][MID]:
                        current_position_from_middle[channel] = True
                    else:
                        current_position_from_middle[channel] = False

                    if last_position_from_middle[channel] is None:
                        last_position_from_middle[channel] = current_position_from_middle[channel]

                    if current_position_from_middle[channel] != last_position_from_middle[channel]:
                        last_position_from_middle[channel] = current_position_from_middle[channel]
                        peak_index[channel] += 1

                    if val_cmp[channel] > WAV_PCM_FORMATS[selected_bits][MID]:
                        val = peaks[channel][peak_index[channel]]
                        frame_tmp = val.to_bytes(WAV_PCM_FORMATS[selected_bits][BYTES], 'little', signed=True)

                    if val_cmp[channel] < WAV_PCM_FORMATS[selected_bits][MID]:
                        val = peaks[channel][peak_index[channel]]
                        frame_tmp = val.to_bytes(WAV_PCM_FORMATS[selected_bits][BYTES], 'little', signed=True)

                    if val_cmp[channel] == WAV_PCM_FORMATS[selected_bits][MID]:
                        val = WAV_PCM_FORMATS[selected_bits][MID]
                        frame_tmp = val.to_bytes(WAV_PCM_FORMATS[selected_bits][BYTES], 'little', signed=True)

                    for byte in frame_tmp:
                        new_frame.append(byte)

                wt.writeframes(new_frame)
        else:
            print("Copy and convert the signal...")
            for i in range(w.getnframes()):
                frame = w.readframes(1)
                new_frame = bytearray()

                for channel in range(0, channels):
                    index = channel * 2
                    frame_cmp = frame[index:index + WAV_PCM_FORMATS[selected_bits][BYTES]]
                    frame_tmp = bytearray()
                    val_cmp = int.from_bytes(frame_cmp, byteorder='little', signed=True)
                    if val_cmp > WAV_PCM_FORMATS[selected_bits][MID]:
                        val = WAV_PCM_FORMATS[selected_bits][MAX]
                        frame_tmp = val.to_bytes(WAV_PCM_FORMATS[selected_bits][BYTES], 'little', signed=True)

                    if val_cmp < WAV_PCM_FORMATS[selected_bits][MID]:
                        val = WAV_PCM_FORMATS[selected_bits][MIN]
                        frame_tmp = val.to_bytes(WAV_PCM_FORMATS[selected_bits][BYTES], 'little', signed=True)

                    if val_cmp == WAV_PCM_FORMATS[selected_bits][MID]:
                        val = WAV_PCM_FORMATS[selected_bits][MID]
                        frame_tmp = val.to_bytes(WAV_PCM_FORMATS[selected_bits][BYTES], 'little', signed=True)

                    for byte in frame_tmp:
                        new_frame.append(byte)
                        
                wt.writeframes(new_frame)

        print("Transformation finished")
        w.close()
        wt.close()

    except Exception as ex:
        print(ex)
