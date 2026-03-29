import { useState, useCallback, useRef } from "react";

const DEFAULT_OPTIONS = {
  maxImageWidth: 800,
  imageQuality: 0.6,
  grayscale: false,
};

/**
 * useDataSaver — manage low-data mode for Bangladeshi students on 2G/3G.
 *
 * Returns:
 *  - dataSaverMode: boolean
 *  - toggleDataSaver: () => void
 *  - compressImage: (file: File) => Promise<File>
 *  - dataUsageKB: number  (rolling total of data saved)
 *  - options: object
 *  - setOptions: React dispatch
 */
export function useDataSaver(initialOptions = {}) {
  const [dataSaverMode, setDataSaverMode] = useState(false);
  const [dataUsageKB, setDataUsageKB] = useState(0);
  const [savedKB, setSavedKB] = useState(0);
  const [options, setOptions] = useState({ ...DEFAULT_OPTIONS, ...initialOptions });
  const canvasRef = useRef(null);

  const toggleDataSaver = useCallback(() => {
    setDataSaverMode((v) => !v);
  }, []);

  /**
   * Compress an image File using the browser Canvas API.
   * Falls back to the original file if compression fails or is not needed.
   *
   * @param {File} file - Image file to compress
   * @returns {Promise<File>} Compressed file (or original)
   */
  const compressImage = useCallback(
    async (file) => {
      if (!dataSaverMode || !file.type.startsWith("image/")) {
        return file;
      }

      return new Promise((resolve) => {
        const reader = new FileReader();
        reader.onload = (e) => {
          const img = new Image();
          img.onload = () => {
            try {
              const canvas = document.createElement("canvas");
              let { width, height } = img;

              // Resize
              if (width > options.maxImageWidth) {
                const ratio = options.maxImageWidth / width;
                width = options.maxImageWidth;
                height = Math.round(height * ratio);
              }

              canvas.width = width;
              canvas.height = height;
              const ctx = canvas.getContext("2d");

              // Grayscale
              if (options.grayscale) {
                ctx.filter = "grayscale(100%)";
              }

              ctx.drawImage(img, 0, 0, width, height);

              canvas.toBlob(
                (blob) => {
                  if (!blob) {
                    resolve(file);
                    return;
                  }
                  const originalKB = file.size / 1024;
                  const compressedKB = blob.size / 1024;
                  const savedNow = Math.max(0, originalKB - compressedKB);

                  setDataUsageKB((v) => v + compressedKB);
                  setSavedKB((v) => v + savedNow);

                  const compressedFile = new File([blob], file.name, {
                    type: "image/jpeg",
                    lastModified: Date.now(),
                  });
                  resolve(compressedFile);
                },
                "image/jpeg",
                options.imageQuality
              );
            } catch {
              resolve(file);
            }
          };
          img.onerror = () => resolve(file);
          img.src = e.target.result;
        };
        reader.onerror = () => resolve(file);
        reader.readAsDataURL(file);
      });
    },
    [dataSaverMode, options]
  );

  /**
   * Track data usage for text responses (UTF-8 byte size).
   * Call this whenever you receive a response chunk.
   */
  const trackResponseBytes = useCallback((text) => {
    const bytes = new TextEncoder().encode(text).length;
    setDataUsageKB((v) => v + bytes / 1024);
  }, []);

  return {
    dataSaverMode,
    toggleDataSaver,
    compressImage,
    trackResponseBytes,
    dataUsageKB: Math.round(dataUsageKB * 10) / 10,
    savedKB: Math.round(savedKB * 10) / 10,
    options,
    setOptions,
  };
}

export default useDataSaver;
