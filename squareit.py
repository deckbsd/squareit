import argparse
import wave

MIN = 1
MID = 2
MAX = 3
BYTES = 0

WAV_PCM_FORMATS = {'8': [1, 0, 128, 255], '16': [2, -32268, 0, 32767], '32': [4, -2147483648, 0, 2147483647]}


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
        w = wave.open(input_file, 'r')
        wt = wave.open(output_file, "w")
        print("Copy parameters ...")

        output_params = w.getparams()
        channels = output_params.nchannels

        wt.setparams(output_params)
        print("Copy and convert the signal...")

        for i in range(w.getnframes()):
            frame = w.readframes(1)
            new_frame = bytearray()

            for channel in range(0, channels):
                index = channel * 2
                frame_cmp = frame[index:index+WAV_PCM_FORMATS[selected_bits][BYTES]]
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
