/**
 * Copyright 2024 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

export type GetAudioContextOptions = AudioContextOptions & {
  id?: string;
};

/**
 * Centralized audio context management and data conversion utilities.
 * 
 * This class implements DRY principles by consolidating audio context creation,
 * caching, and data conversion operations that were previously scattered
 * across multiple functions.
 */
export class AudioContextManager {
  private static contextMap: Map<string, AudioContext> = new Map();
  private static userInteractionPromise: Promise<void> | null = null;

  /**
   * Initialize user interaction promise for audio context creation.
   * This is required for browser autoplay policies.
   */
  private static initializeUserInteraction(): Promise<void> {
    if (!this.userInteractionPromise) {
      this.userInteractionPromise = new Promise((res) => {
        window.addEventListener("pointerdown", res, { once: true });
        window.addEventListener("keydown", res, { once: true });
      });
    }
    return this.userInteractionPromise;
  }

  /**
   * Attempt to create audio context directly with a test audio file.
   * 
   * @returns Promise that resolves if audio can be played immediately
   */
  private static async tryDirectAudioCreation(): Promise<boolean> {
    try {
      const testAudio = new Audio();
      testAudio.src =
        "data:audio/wav;base64,UklGRigAAABXQVZFZm10IBIAAAABAAEARKwAAIhYAQACABAAAABkYXRhAgAAAAEA";
      await testAudio.play();
      return true;
    } catch {
      return false;
    }
  }

  /**
   * Create or retrieve a cached AudioContext with the given options.
   * 
   * @param options Audio context options including optional ID for caching
   * @returns Promise resolving to AudioContext instance
   */
  static async getAudioContext(options?: GetAudioContextOptions): Promise<AudioContext> {
    // Check if we have a cached context for this ID
    if (options?.id && this.contextMap.has(options.id)) {
      const cachedContext = this.contextMap.get(options.id);
      if (cachedContext) {
        return cachedContext;
      }
    }

    // Try to create context directly first
    const canPlayDirectly = await this.tryDirectAudioCreation();
    
    if (!canPlayDirectly) {
      // Wait for user interaction if direct creation failed
      await this.initializeUserInteraction();
    }

    // Create new audio context
    const context = new AudioContext(options);
    
    // Cache the context if an ID was provided
    if (options?.id) {
      this.contextMap.set(options.id, context);
    }

    return context;
  }

  /**
   * Clear a cached audio context by ID.
   * 
   * @param id Context ID to clear
   */
  static clearCachedContext(id: string): void {
    const context = this.contextMap.get(id);
    if (context) {
      context.close();
      this.contextMap.delete(id);
    }
  }

  /**
   * Clear all cached audio contexts.
   */
  static clearAllContexts(): void {
    this.contextMap.forEach(context => context.close());
    this.contextMap.clear();
  }
}

/**
 * Utility class for data format conversions.
 * 
 * Centralizes common data conversion operations to eliminate
 * code duplication across the application.
 */
export class DataConverter {
  /**
   * Convert a Blob to JSON object.
   * 
   * @param blob Blob containing JSON data
   * @returns Promise resolving to parsed JSON object
   */
  static blobToJSON(blob: Blob): Promise<any> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => {
        if (reader.result) {
          try {
            const json = JSON.parse(reader.result as string);
            resolve(json);
          } catch (error) {
            reject(new Error(`Failed to parse JSON: ${error}`));
          }
        } else {
          reject(new Error("FileReader result is null"));
        }
      };
      reader.onerror = () => reject(new Error("Failed to read blob"));
      reader.readAsText(blob);
    });
  }

  /**
   * Convert base64 string to ArrayBuffer.
   * 
   * @param base64 Base64 encoded string
   * @returns ArrayBuffer containing decoded data
   */
  static base64ToArrayBuffer(base64: string): ArrayBuffer {
    const binaryString = atob(base64);
    const bytes = new Uint8Array(binaryString.length);
    
    for (let i = 0; i < binaryString.length; i++) {
      bytes[i] = binaryString.charCodeAt(i);
    }
    
    return bytes.buffer;
  }

  /**
   * Convert ArrayBuffer to base64 string.
   * 
   * @param buffer ArrayBuffer to encode
   * @returns Base64 encoded string
   */
  static arrayBufferToBase64(buffer: ArrayBuffer): string {
    const bytes = new Uint8Array(buffer);
    let binary = '';
    
    for (let i = 0; i < bytes.byteLength; i++) {
      binary += String.fromCharCode(bytes[i]);
    }
    
    return btoa(binary);
  }

  /**
   * Convert Uint8Array to base64 string.
   * 
   * @param uint8Array Uint8Array to encode
   * @returns Base64 encoded string
   */
  static uint8ArrayToBase64(uint8Array: Uint8Array): string {
    return this.arrayBufferToBase64(uint8Array.buffer);
  }
}

// Backward compatibility exports - delegate to class methods
export const audioContext = AudioContextManager.getAudioContext;
export const blobToJSON = DataConverter.blobToJSON;
export const base64ToArrayBuffer = DataConverter.base64ToArrayBuffer;

// Additional utility exports from the new classes
export const arrayBufferToBase64 = DataConverter.arrayBufferToBase64;
export const uint8ArrayToBase64 = DataConverter.uint8ArrayToBase64;
