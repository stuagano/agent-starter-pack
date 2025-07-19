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

import { AudioContextManager, DataConverter, audioContext, blobToJSON, base64ToArrayBuffer } from '../utils';

// Mock the Audio constructor for testing
global.Audio = jest.fn().mockImplementation(() => ({
  play: jest.fn().mockResolvedValue(undefined),
  src: '',
}));

// Mock window methods
Object.defineProperty(window, 'addEventListener', {
  value: jest.fn(),
  writable: true,
});

// Mock AudioContext
global.AudioContext = jest.fn().mockImplementation(() => ({
  close: jest.fn().mockResolvedValue(undefined),
  state: 'running',
}));

// Mock btoa and atob
global.btoa = jest.fn((str: string) => Buffer.from(str, 'binary').toString('base64'));
global.atob = jest.fn((str: string) => Buffer.from(str, 'base64').toString('binary'));

describe('AudioContextManager', () => {
  beforeEach(() => {
    // Clear the internal map before each test
    AudioContextManager.clearAllContexts();
    jest.clearAllMocks();
  });

  describe('getAudioContext', () => {
    it('should create a new AudioContext when audio can be played directly', async () => {
      const mockAudio = {
        play: jest.fn().mockResolvedValue(undefined),
        src: '',
      };
      (global.Audio as jest.Mock).mockImplementation(() => mockAudio);

      const context = await AudioContextManager.getAudioContext();

      expect(global.AudioContext).toHaveBeenCalledTimes(1);
      expect(context).toBeDefined();
    });

    it('should wait for user interaction when direct audio creation fails', async () => {
      const mockAudio = {
        play: jest.fn().mockRejectedValue(new Error('Autoplay prevented')),
        src: '',
      };
      (global.Audio as jest.Mock).mockImplementation(() => mockAudio);

      let userInteractionResolve: () => void;
      const userInteractionPromise = new Promise<void>((resolve) => {
        userInteractionResolve = resolve;
      });

      (window.addEventListener as jest.Mock).mockImplementation((event: string, handler: () => void) => {
        if (event === 'pointerdown') {
          // Simulate user interaction after a short delay
          setTimeout(() => {
            handler();
            userInteractionResolve();
          }, 10);
        }
      });

      const contextPromise = AudioContextManager.getAudioContext();
      
      // The promise should not resolve immediately
      await expect(Promise.race([
        contextPromise,
        new Promise((_, reject) => setTimeout(() => reject(new Error('Too fast')), 5))
      ])).rejects.toThrow('Too fast');

      // Wait for user interaction to be triggered
      await userInteractionPromise;
      
      const context = await contextPromise;
      expect(context).toBeDefined();
      expect(global.AudioContext).toHaveBeenCalledTimes(1);
    });

    it('should cache AudioContext when ID is provided', async () => {
      const contextId = 'test-context';
      const options = { id: contextId, sampleRate: 44100 };

      const context1 = await AudioContextManager.getAudioContext(options);
      const context2 = await AudioContextManager.getAudioContext(options);

      // Should return the same cached instance
      expect(context1).toBe(context2);
      expect(global.AudioContext).toHaveBeenCalledTimes(1);
      expect(global.AudioContext).toHaveBeenCalledWith(options);
    });

    it('should create different contexts for different IDs', async () => {
      const context1 = await AudioContextManager.getAudioContext({ id: 'context1' });
      const context2 = await AudioContextManager.getAudioContext({ id: 'context2' });

      expect(context1).not.toBe(context2);
      expect(global.AudioContext).toHaveBeenCalledTimes(2);
    });

    it('should create new context when no ID is provided', async () => {
      const context1 = await AudioContextManager.getAudioContext();
      const context2 = await AudioContextManager.getAudioContext();

      expect(context1).not.toBe(context2);
      expect(global.AudioContext).toHaveBeenCalledTimes(2);
    });
  });

  describe('clearCachedContext', () => {
    it('should clear and close a specific cached context', async () => {
      const contextId = 'test-context';
      const mockClose = jest.fn().mockResolvedValue(undefined);
      
      (global.AudioContext as jest.Mock).mockImplementation(() => ({
        close: mockClose,
        state: 'running',
      }));

      const context = await AudioContextManager.getAudioContext({ id: contextId });
      
      AudioContextManager.clearCachedContext(contextId);
      
      expect(mockClose).toHaveBeenCalledTimes(1);
      
      // Should create a new context if requested again
      const newContext = await AudioContextManager.getAudioContext({ id: contextId });
      expect(newContext).not.toBe(context);
      expect(global.AudioContext).toHaveBeenCalledTimes(2);
    });

    it('should handle clearing non-existent context gracefully', () => {
      expect(() => {
        AudioContextManager.clearCachedContext('non-existent');
      }).not.toThrow();
    });
  });

  describe('clearAllContexts', () => {
    it('should clear and close all cached contexts', async () => {
      const mockClose = jest.fn().mockResolvedValue(undefined);
      
      (global.AudioContext as jest.Mock).mockImplementation(() => ({
        close: mockClose,
        state: 'running',
      }));

      await AudioContextManager.getAudioContext({ id: 'context1' });
      await AudioContextManager.getAudioContext({ id: 'context2' });
      
      AudioContextManager.clearAllContexts();
      
      expect(mockClose).toHaveBeenCalledTimes(2);
    });
  });
});

describe('DataConverter', () => {
  describe('blobToJSON', () => {
    it('should convert blob to JSON object', async () => {
      const testData = { test: 'data', number: 42 };
      const jsonString = JSON.stringify(testData);
      
      const mockBlob = new Blob([jsonString], { type: 'application/json' });
      
      const result = await DataConverter.blobToJSON(mockBlob);
      
      expect(result).toEqual(testData);
    });

    it('should reject with error when blob contains invalid JSON', async () => {
      const mockBlob = new Blob(['invalid json {'], { type: 'application/json' });
      
      await expect(DataConverter.blobToJSON(mockBlob)).rejects.toThrow('Failed to parse JSON');
    });

    it('should reject when FileReader result is null', async () => {
      const mockBlob = new Blob(['test'], { type: 'application/json' });
      
      // Mock FileReader to return null result
      const originalFileReader = global.FileReader;
      global.FileReader = jest.fn().mockImplementation(() => ({
        readAsText: jest.fn(),
        onload: null,
        onerror: null,
        result: null,
      }));

      const promise = DataConverter.blobToJSON(mockBlob);
      
      // Simulate FileReader onload with null result
      const readerInstance = (global.FileReader as jest.Mock).mock.instances[0];
      readerInstance.onload();
      
      await expect(promise).rejects.toThrow('FileReader result is null');
      
      global.FileReader = originalFileReader;
    });
  });

  describe('base64ToArrayBuffer', () => {
    it('should convert base64 string to ArrayBuffer', () => {
      const testString = 'Hello, World!';
      const base64String = btoa(testString);
      
      const result = DataConverter.base64ToArrayBuffer(base64String);
      const resultString = new TextDecoder().decode(result);
      
      expect(resultString).toBe(testString);
      expect(result).toBeInstanceOf(ArrayBuffer);
    });

    it('should handle empty base64 string', () => {
      const result = DataConverter.base64ToArrayBuffer('');
      
      expect(result).toBeInstanceOf(ArrayBuffer);
      expect(result.byteLength).toBe(0);
    });
  });

  describe('arrayBufferToBase64', () => {
    it('should convert ArrayBuffer to base64 string', () => {
      const testString = 'Hello, World!';
      const buffer = new TextEncoder().encode(testString).buffer;
      
      const result = DataConverter.arrayBufferToBase64(buffer);
      const expectedBase64 = btoa(testString);
      
      expect(result).toBe(expectedBase64);
    });

    it('should handle empty ArrayBuffer', () => {
      const buffer = new ArrayBuffer(0);
      
      const result = DataConverter.arrayBufferToBase64(buffer);
      
      expect(result).toBe('');
    });
  });

  describe('uint8ArrayToBase64', () => {
    it('should convert Uint8Array to base64 string', () => {
      const testString = 'Hello, World!';
      const uint8Array = new TextEncoder().encode(testString);
      
      const result = DataConverter.uint8ArrayToBase64(uint8Array);
      const expectedBase64 = btoa(testString);
      
      expect(result).toBe(expectedBase64);
    });

    it('should handle empty Uint8Array', () => {
      const uint8Array = new Uint8Array(0);
      
      const result = DataConverter.uint8ArrayToBase64(uint8Array);
      
      expect(result).toBe('');
    });
  });
});

describe('Backward Compatibility', () => {
  it('should maintain backward compatibility for audioContext function', async () => {
    const result = await audioContext();
    
    expect(result).toBeDefined();
    expect(global.AudioContext).toHaveBeenCalled();
  });

  it('should maintain backward compatibility for blobToJSON function', async () => {
    const testData = { test: 'data' };
    const mockBlob = new Blob([JSON.stringify(testData)], { type: 'application/json' });
    
    const result = await blobToJSON(mockBlob);
    
    expect(result).toEqual(testData);
  });

  it('should maintain backward compatibility for base64ToArrayBuffer function', () => {
    const testString = 'Hello, World!';
    const base64String = btoa(testString);
    
    const result = base64ToArrayBuffer(base64String);
    const resultString = new TextDecoder().decode(result);
    
    expect(resultString).toBe(testString);
  });
});

describe('Integration Tests', () => {
  it('should work with real-world audio context scenarios', async () => {
    // Test creating multiple contexts with different configurations
    const micContext = await AudioContextManager.getAudioContext({ 
      id: 'microphone',
      sampleRate: 16000 
    });
    
    const speakerContext = await AudioContextManager.getAudioContext({ 
      id: 'speaker',
      sampleRate: 44100 
    });
    
    expect(micContext).not.toBe(speakerContext);
    expect(global.AudioContext).toHaveBeenCalledWith({ id: 'microphone', sampleRate: 16000 });
    expect(global.AudioContext).toHaveBeenCalledWith({ id: 'speaker', sampleRate: 44100 });
  });

  it('should handle data conversion pipeline', () => {
    const originalData = 'Test data for conversion pipeline';
    
    // String -> ArrayBuffer -> Base64 -> ArrayBuffer -> String
    const arrayBuffer1 = new TextEncoder().encode(originalData).buffer;
    const base64String = DataConverter.arrayBufferToBase64(arrayBuffer1);
    const arrayBuffer2 = DataConverter.base64ToArrayBuffer(base64String);
    const finalString = new TextDecoder().decode(arrayBuffer2);
    
    expect(finalString).toBe(originalData);
  });

  it('should handle complex multimodal data scenarios', async () => {
    // Simulate a complex scenario with multiple data conversions
    const textData = 'Complex multimodal data';
    const imageData = new Uint8Array([0xFF, 0xD8, 0xFF, 0xE0]); // JPEG header
    
    // Convert image to base64
    const imageBase64 = DataConverter.uint8ArrayToBase64(imageData);
    
    // Create a JSON blob with mixed content
    const mixedContent = {
      text: textData,
      image: imageBase64,
      metadata: { type: 'multimodal', timestamp: Date.now() }
    };
    
    const jsonBlob = new Blob([JSON.stringify(mixedContent)], { type: 'application/json' });
    
    // Convert back from blob
    const parsedContent = await DataConverter.blobToJSON(jsonBlob);
    
    expect(parsedContent.text).toBe(textData);
    expect(parsedContent.image).toBe(imageBase64);
    expect(parsedContent.metadata.type).toBe('multimodal');
    
    // Verify image data roundtrip
    const recoveredImageData = DataConverter.base64ToArrayBuffer(parsedContent.image);
    const recoveredImageUint8 = new Uint8Array(recoveredImageData);
    
    expect(recoveredImageUint8).toEqual(imageData);
  });
});