import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import MovieCard from '@/components/MovieCard';

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

describe('MovieCard Component', () => {
  // Sample movie data for testing
  const mockMovie = {
    tmdb_id: 550,
    title: 'Fight Club',
    poster_path: '/path/to/poster.jpg',
    vote_average: 8.8,
    release_date: '1999-10-15',
    runtime: 139,
  };

  // Test 1: Verifies that the component renders the movie title and release year correctly
  it('renders movie title and year correctly', () => {
    render(<MovieCard movie={mockMovie} />);

    // Check that the title is rendered
    expect(screen.getByText('Fight Club')).toBeInTheDocument();

    // Check that the year is extracted and displayed from the release_date
    expect(screen.getByText('1999')).toBeInTheDocument();
  });

  // Test 2: Verifies that the rating badge displays when vote_average is greater than 0
  it('renders rating badge when vote_average > 0', () => {
    render(<MovieCard movie={mockMovie} />);

    // The vote_average (8.8) should be displayed as a rating
    expect(screen.getByText('8.8')).toBeInTheDocument();
  });

  // Test 3: Verifies that the component links to the correct movie detail page using tmdb_id
  it('links to correct movie detail page using tmdb_id', () => {
    render(<MovieCard movie={mockMovie} />);

    // The link should navigate to /movie/{tmdb_id}
    const movieLink = screen.getByRole('link');
    expect(movieLink).toHaveAttribute('href', '/movie/550');
  });

  // Test 4: Verifies that no rating is shown when vote_average is 0 or not available
  it('does not render rating badge when vote_average is 0', () => {
    const movieWithoutRating = { ...mockMovie, vote_average: 0 };
    render(<MovieCard movie={movieWithoutRating} />);

    // The zero rating should not be displayed as a badge
    const badgeElement = screen.queryByText('0');
    expect(badgeElement).not.toBeInTheDocument();
  });

  // Test 5: Verifies that the poster image is rendered with correct attributes
  it('renders poster image with correct attributes', () => {
    render(<MovieCard movie={mockMovie} />);

    // The poster image should be rendered
    const posterImage = screen.getByAltText('Fight Club');
    expect(posterImage).toBeInTheDocument();
    expect(posterImage).toHaveAttribute('src', expect.stringContaining('poster'));
  });

  // Test 6: Verifies that the runtime is displayed correctly
  it('renders runtime correctly', () => {
    render(<MovieCard movie={mockMovie} />);

    // The runtime (139 minutes) should be displayed
    expect(screen.getByText(/139/)).toBeInTheDocument();
  });

  // Test 7: Verifies that different size variants can be applied
  it('applies size variant classes correctly', () => {
    const { container } = render(<MovieCard movie={mockMovie} size="lg" />);

    // Check that the size variant is applied to the component
    const cardElement = container.firstChild;
    expect(cardElement).toHaveClass(expect.stringContaining('lg'));
  });

  // Test 8: Verifies that overview can be shown when showOverview prop is true
  it('shows overview when showOverview prop is true', () => {
    const movieWithOverview = {
      ...mockMovie,
      overview: 'An insomniac office worker and a devil-may-care soapmaker form an underground fight club.',
    };
    render(<MovieCard movie={movieWithOverview} showOverview={true} />);

    // The overview should be visible
    expect(screen.getByText(/An insomniac office worker/)).toBeInTheDocument();
  });
});
