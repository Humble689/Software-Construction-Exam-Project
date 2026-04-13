import '@testing-library/jest-dom';
import { moviesAPI, tokenManager } from '@/lib/api';

// Mock the global fetch function
global.fetch = jest.fn();

// Mock next/navigation to avoid errors in test environment
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
    replace: jest.fn(),
    back: jest.fn(),
    forward: jest.fn(),
    refresh: jest.fn(),
  }),
  usePathname: () => '/',
  useSearchParams: () => new URLSearchParams(),
}));

describe('API Module', () => {
  beforeEach(() => {
    // Clear all mocks before each test
    jest.clearAllMocks();
    // Clear localStorage before each test
    localStorage.clear();
  });

  describe('moviesAPI.search', () => {
    // Test 1: Verifies that the search method constructs the correct API URL with query parameters
    it('constructs correct URL for search request', async () => {
      const mockFetch = global.fetch as jest.Mock;
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ results: [] }),
      });

      // Call the search method
      await moviesAPI.search('Inception');

      // Verify fetch was called with the correct URL
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/search'),
        expect.any(Object)
      );

      // Verify the query parameter is included
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('query=Inception'),
        expect.any(Object)
      );
    });

    // Test 2: Verifies that the search method includes the API key in the request
    it('includes API key in search request', async () => {
      const mockFetch = global.fetch as jest.Mock;
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ results: [] }),
      });

      await moviesAPI.search('Interstellar');

      // Verify the API key is included in the URL or headers
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('api_key'),
        expect.any(Object)
      );
    });

    // Test 3: Verifies that the search method returns movie results
    it('returns movie results from API response', async () => {
      const mockFetch = global.fetch as jest.Mock;
      const mockResults = [
        { id: 1, title: 'Inception', vote_average: 8.8 },
        { id: 2, title: 'Interstellar', vote_average: 8.6 },
      ];

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ results: mockResults }),
      });

      const results = await moviesAPI.search('Christopher Nolan');

      // Verify the results are returned
      expect(results).toEqual(mockResults);
    });

    // Test 4: Verifies error handling when the API request fails
    it('throws error when API request fails', async () => {
      const mockFetch = global.fetch as jest.Mock;
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
      });

      // The search should handle the error appropriately
      await expect(moviesAPI.search('Test')).rejects.toThrow();
    });

    // Test 5: Verifies that the search URL includes pagination parameters
    it('includes pagination parameters in search URL', async () => {
      const mockFetch = global.fetch as jest.Mock;
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ results: [] }),
      });

      await moviesAPI.search('Avatar', 2);

      // Verify page parameter is included
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('page=2'),
        expect.any(Object)
      );
    });
  });

  describe('Token Management', () => {
    // Test 6: Verifies that setTokens correctly stores tokens in localStorage
    it('setTokens stores tokens in localStorage', () => {
      const accessToken = 'mock_access_token_12345';
      const refreshToken = 'mock_refresh_token_67890';

      tokenManager.setTokens(accessToken, refreshToken);

      // Verify tokens are stored in localStorage
      expect(localStorage.getItem('accessToken')).toBe(accessToken);
      expect(localStorage.getItem('refreshToken')).toBe(refreshToken);
    });

    // Test 7: Verifies that loadTokens retrieves previously stored tokens
    it('loadTokens retrieves stored tokens from localStorage', () => {
      const accessToken = 'test_access_token';
      const refreshToken = 'test_refresh_token';

      // First set the tokens
      tokenManager.setTokens(accessToken, refreshToken);

      // Then load them
      const tokens = tokenManager.loadTokens();

      // Verify the correct tokens are retrieved
      expect(tokens.accessToken).toBe(accessToken);
      expect(tokens.refreshToken).toBe(refreshToken);
    });

    // Test 8: Verifies that loadTokens returns null tokens when none are stored
    it('loadTokens returns null when no tokens are stored', () => {
      // Make sure localStorage is empty
      localStorage.clear();

      const tokens = tokenManager.loadTokens();

      // Both tokens should be null
      expect(tokens.accessToken).toBeNull();
      expect(tokens.refreshToken).toBeNull();
    });

    // Test 9: Verifies that clearTokens removes all tokens from localStorage
    it('clearTokens removes tokens from localStorage', () => {
      const accessToken = 'token_to_clear';
      const refreshToken = 'refresh_to_clear';

      // Set tokens first
      tokenManager.setTokens(accessToken, refreshToken);
      expect(localStorage.getItem('accessToken')).toBe(accessToken);

      // Clear tokens
      tokenManager.clearTokens();

      // Verify tokens are removed
      expect(localStorage.getItem('accessToken')).toBeNull();
      expect(localStorage.getItem('refreshToken')).toBeNull();
    });

    // Test 10: Verifies that setTokens overwrites previous tokens
    it('setTokens overwrites previous tokens', () => {
      const oldAccessToken = 'old_access_token';
      const newAccessToken = 'new_access_token';
      const refreshToken = 'refresh_token';

      // Set initial tokens
      tokenManager.setTokens(oldAccessToken, refreshToken);
      expect(localStorage.getItem('accessToken')).toBe(oldAccessToken);

      // Set new tokens
      tokenManager.setTokens(newAccessToken, refreshToken);

      // Verify old token is overwritten
      expect(localStorage.getItem('accessToken')).toBe(newAccessToken);
      expect(localStorage.getItem('refreshToken')).toBe(refreshToken);
    });

    // Test 11: Verifies that token operations handle edge cases (empty strings)
    it('handles empty string tokens correctly', () => {
      tokenManager.setTokens('', '');

      const tokens = tokenManager.loadTokens();
      expect(tokens.accessToken).toBe('');
      expect(tokens.refreshToken).toBe('');
    });
  });

  describe('moviesAPI integration', () => {
    // Test 12: Verifies that API requests include authentication tokens in headers
    it('includes authorization token in API headers', async () => {
      const mockFetch = global.fetch as jest.Mock;
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ results: [] }),
      });

      // Set a token first
      tokenManager.setTokens('test_token_123', 'refresh_123');

      // Make an API call
      await moviesAPI.search('Test Movie');

      // Verify the token is included in headers
      expect(mockFetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          headers: expect.objectContaining({
            Authorization: expect.stringContaining('test_token_123'),
          }),
        })
      );
    });

    // Test 13: Verifies that fetch errors are handled properly
    it('handles network errors gracefully', async () => {
      const mockFetch = global.fetch as jest.Mock;
      mockFetch.mockRejectedValueOnce(new Error('Network error'));

      // Should throw or handle error gracefully
      await expect(moviesAPI.search('Test')).rejects.toThrow('Network error');
    });
  });
});
