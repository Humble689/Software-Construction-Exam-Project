import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import SearchModal from '@/components/SearchModal';

// Mock next/link
jest.mock('next/link', () => {
  return ({ children, href }: { children: React.ReactNode; href: string }) => (
    <a href={href}>{children}</a>
  );
});

// Mock next/image
jest.mock('next/image', () => ({
  __esModule: true,
  default: (props: any) => {
    // eslint-disable-next-line jsx-a11y/alt-text
    return <img {...props} />;
  },
}));

describe('SearchModal Component', () => {
  // Test 1: Verifies that the modal renders nothing (is not visible) when open prop is false
  it('renders nothing when open is false', () => {
    const mockOnClose = jest.fn();
    const { container } = render(
      <SearchModal open={false} onClose={mockOnClose} />
    );

    // The modal container should not be in the document or should be hidden
    const modal = container.querySelector('[role="dialog"]');
    expect(modal).not.toBeInTheDocument();
  });

  // Test 2: Verifies that the search input field is rendered and accessible when open is true
  it('renders search input when open is true', () => {
    const mockOnClose = jest.fn();
    render(<SearchModal open={true} onClose={mockOnClose} />);

    // The search input should be visible in the DOM
    const searchInput = screen.getByPlaceholderText(/search|query|find/i);
    expect(searchInput).toBeInTheDocument();
    expect(searchInput).toBeVisible();
  });

  // Test 3: Verifies that the onClose callback is invoked when the ESC key is pressed
  it('calls onClose when ESC is pressed', async () => {
    const mockOnClose = jest.fn();
    render(<SearchModal open={true} onClose={mockOnClose} />);

    // Simulate pressing the ESC key
    fireEvent.keyDown(document, { key: 'Escape', code: 'Escape' });

    // The onClose callback should have been called
    expect(mockOnClose).toHaveBeenCalledTimes(1);
  });

  // Test 4: Verifies that the search input can be typed into
  it('allows typing in the search input', async () => {
    const mockOnClose = jest.fn();
    render(<SearchModal open={true} onClose={mockOnClose} />);

    const searchInput = screen.getByPlaceholderText(/search|query|find/i) as HTMLInputElement;

    // Type search text
    await userEvent.type(searchInput, 'Inception');

    // Verify the input has the typed value
    expect(searchInput.value).toBe('Inception');
  });

  // Test 5: Verifies that the close button is present and functional
  it('renders close button that calls onClose', async () => {
    const mockOnClose = jest.fn();
    render(<SearchModal open={true} onClose={mockOnClose} />);

    // Find the close button (usually an X button or close label)
    const closeButton = screen.getByRole('button', { name: /close|dismiss|x/i });
    expect(closeButton).toBeInTheDocument();

    // Click the close button
    await userEvent.click(closeButton);

    // The onClose callback should have been called
    expect(mockOnClose).toHaveBeenCalledTimes(1);
  });

  // Test 6: Verifies that the modal stays open when clicking inside it
  it('does not close when clicking inside the modal', async () => {
    const mockOnClose = jest.fn();
    render(<SearchModal open={true} onClose={mockOnClose} />);

    const searchInput = screen.getByPlaceholderText(/search|query|find/i);

    // Click inside the modal
    await userEvent.click(searchInput);

    // The onClose callback should NOT be called
    expect(mockOnClose).not.toHaveBeenCalled();
  });

  // Test 7: Verifies that the modal closes when clicking on the backdrop/overlay
  it('calls onClose when clicking on the backdrop', async () => {
    const mockOnClose = jest.fn();
    const { container } = render(
      <SearchModal open={true} onClose={mockOnClose} />
    );

    // Find the backdrop element and click it
    const backdrop = container.querySelector('[role="dialog"]')?.parentElement;
    if (backdrop) {
      await userEvent.click(backdrop);
      expect(mockOnClose).toHaveBeenCalled();
    }
  });

  // Test 8: Verifies that search results can be displayed (if component renders results)
  it('displays search results when available', () => {
    const mockOnClose = jest.fn();
    const mockResults = [
      { id: 1, title: 'Inception' },
      { id: 2, title: 'Interstellar' },
    ];

    render(
      <SearchModal
        open={true}
        onClose={mockOnClose}
        results={mockResults}
      />
    );

    // Check if results are displayed
    expect(screen.getByText('Inception')).toBeInTheDocument();
    expect(screen.getByText('Interstellar')).toBeInTheDocument();
  });

  // Test 9: Verifies that the search input is focused when the modal opens
  it('focuses search input when modal opens', async () => {
    const mockOnClose = jest.fn();
    render(<SearchModal open={true} onClose={mockOnClose} />);

    const searchInput = screen.getByPlaceholderText(/search|query|find/i);

    // The input should be focused (autoFocus attribute)
    expect(searchInput).toHaveFocus();
  });
});
