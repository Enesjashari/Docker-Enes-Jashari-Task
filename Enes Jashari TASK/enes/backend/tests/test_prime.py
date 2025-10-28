import pytest
from app.utils import is_prime, count_primes_in_range, split_into_chunks


class TestIsPrime:
    """Test cases for the is_prime function."""
    
    def test_is_prime_with_small_primes(self):
        """Test that small prime numbers are correctly identified."""
        primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
        for num in primes:
            assert is_prime(num), f"{num} should be prime"
    
    def test_is_prime_with_non_primes(self):
        """Test that non-prime numbers are correctly identified."""
        non_primes = [0, 1, 4, 6, 8, 9, 10, 12, 15, 16, 18, 20]
        for num in non_primes:
            assert not is_prime(num), f"{num} should not be prime"
    
    def test_is_prime_with_larger_primes(self):
        """Test with larger prime numbers."""
        large_primes = [97, 101, 103, 107, 109, 113]
        for num in large_primes:
            assert is_prime(num), f"{num} should be prime"
    
    def test_is_prime_with_larger_non_primes(self):
        """Test with larger non-prime numbers."""
        large_non_primes = [100, 102, 104, 105, 106, 108]
        for num in large_non_primes:
            assert not is_prime(num), f"{num} should not be prime"
    
    def test_is_prime_edge_cases(self):
        """Test edge cases."""
        assert not is_prime(0)
        assert not is_prime(1)
        assert is_prime(2)
        assert not is_prime(-5)


class TestCountPrimesInRange:
    """Test cases for the count_primes_in_range function."""
    
    def test_count_primes_small_range(self):
        """Test counting primes in a small range."""
        # Primes from 1 to 10: 2, 3, 5, 7
        assert count_primes_in_range(1, 10) == 4
    
    def test_count_primes_medium_range(self):
        """Test counting primes in a medium range."""
        # Primes from 1 to 100: 25 primes
        assert count_primes_in_range(1, 100) == 25
    
    def test_count_primes_single_number(self):
        """Test counting primes for a single number."""
        assert count_primes_in_range(7, 7) == 1
        assert count_primes_in_range(8, 8) == 0
    
    def test_count_primes_range_with_no_primes(self):
        """Test a range with no primes."""
        assert count_primes_in_range(8, 10) == 0
    
    def test_count_primes_range_starting_from_middle(self):
        """Test counting primes from a non-zero start."""
        # Primes from 10 to 20: 11, 13, 17, 19
        assert count_primes_in_range(10, 20) == 4


class TestSplitIntoChunks:
    """Test cases for the split_into_chunks function."""
    
    def test_split_even_division(self):
        """Test splitting when n divides evenly by chunks."""
        chunks = split_into_chunks(100, 4)
        assert len(chunks) == 4
        assert chunks[0] == (1, 25)
        assert chunks[1] == (26, 50)
        assert chunks[2] == (51, 75)
        assert chunks[3] == (76, 100)
    
    def test_split_uneven_division(self):
        """Test splitting when n doesn't divide evenly."""
        chunks = split_into_chunks(100, 3)
        assert len(chunks) == 3
        assert chunks[0] == (1, 33)
        assert chunks[1] == (34, 66)
        assert chunks[2] == (67, 100)  # Last chunk gets remainder
    
    def test_split_single_chunk(self):
        """Test with a single chunk."""
        chunks = split_into_chunks(100, 1)
        assert len(chunks) == 1
        assert chunks[0] == (1, 100)
    
    def test_split_many_chunks(self):
        """Test with many chunks."""
        chunks = split_into_chunks(1000, 16)
        assert len(chunks) == 16
        # Verify all numbers are covered
        assert chunks[0][0] == 1
        assert chunks[-1][1] == 1000
        # Verify no gaps
        for i in range(len(chunks) - 1):
            assert chunks[i][1] + 1 == chunks[i + 1][0]
    
    def test_split_coverage(self):
        """Test that all chunks cover the full range without gaps or overlaps."""
        chunks = split_into_chunks(200000, 16)
        
        # Check first chunk starts at 1
        assert chunks[0][0] == 1
        
        # Check last chunk ends at n
        assert chunks[-1][1] == 200000
        
        # Check no gaps between chunks
        for i in range(len(chunks) - 1):
            assert chunks[i][1] + 1 == chunks[i + 1][0], \
                f"Gap between chunk {i} and {i+1}"
        
        # Calculate total coverage
        total_numbers = sum(end - start + 1 for start, end in chunks)
        assert total_numbers == 200000


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

