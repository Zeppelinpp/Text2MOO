#!/usr/bin/env python3
"""Test script for DataConvertor functionality."""

import json
import polars as pl
from pathlib import Path
from text2moo.interface.data_convertor import DataConvertor, DataConvertorError

def create_test_excel():
    """Create a test Excel file with valid data."""
    # Create test data
    data = {
        'id': ['001', '002', '003', '004'],
        'name': ['Item A', 'Item B', 'Item C', 'Item D'],
        'weight': [1.5, 2.3, 0.8, 3.1],
        'cost': [100, 150, 80, 200],
        'priority': [3, 1, 2, 1]
    }
    
    # Create DataFrame and save to Excel
    df = pl.DataFrame(data)
    test_file = Path('test_data.xlsx')
    df.write_excel(test_file)
    return test_file

def create_invalid_excel():
    """Create test Excel files with invalid data."""
    # Missing ID column
    data_no_id = {
        'name': ['Item A', 'Item B'],
        'weight': [1.5, 2.3],
        'cost': [100, 150]
    }
    df_no_id = pl.DataFrame(data_no_id)
    no_id_file = Path('test_no_id.xlsx')
    df_no_id.write_excel(no_id_file)
    
    # Duplicate IDs
    data_dup_id = {
        'id': ['001', '001', '002'],
        'name': ['Item A', 'Item B', 'Item C'],
        'weight': [1.5, 2.3, 0.8]
    }
    df_dup_id = pl.DataFrame(data_dup_id)
    dup_id_file = Path('test_dup_id.xlsx')
    df_dup_id.write_excel(dup_id_file)
    
    # Missing name column
    data_no_name = {
        'id': ['001', '002'],
        'weight': [1.5, 2.3]
    }
    df_no_name = pl.DataFrame(data_no_name)
    no_name_file = Path('test_no_name.xlsx')
    df_no_name.write_excel(no_name_file)
    
    return no_id_file, dup_id_file, no_name_file

def test_valid_conversion():
    """Test conversion of valid Excel data."""
    print("Testing valid Excel conversion...")
    test_file = create_test_excel()
    
    try:
        # Create convertor and convert data
        convertor = DataConvertor()
        result = convertor.convert(test_file)
        
        print("✓ Conversion successful!")
        print(f"  - Unit attributes: {result.unit_attr}")
        print(f"  - Number of units: {len(result.units)}")
        
        # Check first unit
        if result.units:
            first_unit = result.units[0]
            print(f"  - First unit: ID={first_unit.id}, Name={first_unit.name}")
            print(f"    Attributes: {first_unit.attributes}")
        
        # Verify attributes
        expected_attrs = ['weight', 'cost', 'priority']
        assert set(result.unit_attr) == set(expected_attrs), f"Expected attributes {expected_attrs}, got {result.unit_attr}"
        
        # Verify all units have IDs and names
        for unit in result.units:
            assert unit.id is not None, "Unit missing ID"
            assert unit.name is not None, "Unit missing name"
            assert len(unit.attributes) == len(expected_attrs), f"Unit {unit.id} has wrong number of attributes"
        
        print("✓ All validations passed!")
        
    finally:
        # Clean up
        test_file.unlink(missing_ok=True)

def test_invalid_conversions():
    """Test handling of invalid Excel data."""
    print("\nTesting invalid Excel conversions...")
    no_id_file, dup_id_file, no_name_file = create_invalid_excel()
    
    convertor = DataConvertor()
    
    # Test missing ID column
    try:
        convertor.convert(no_id_file)
        print("✗ Missing ID validation failed - conversion should have raised error")
    except DataConvertorError as e:
        print(f"✓ Missing ID correctly caught: {e}")
    finally:
        no_id_file.unlink(missing_ok=True)
    
    # Test duplicate IDs
    try:
        convertor.convert(dup_id_file)
        print("✗ Duplicate ID validation failed - conversion should have raised error")
    except DataConvertorError as e:
        print(f"✓ Duplicate ID correctly caught: {e}")
    finally:
        dup_id_file.unlink(missing_ok=True)
    
    # Test missing name column
    try:
        convertor.convert(no_name_file)
        print("✗ Missing name validation failed - conversion should have raised error")
    except DataConvertorError as e:
        print(f"✓ Missing name correctly caught: {e}")
    finally:
        no_name_file.unlink(missing_ok=True)

def test_nonexistent_file():
    """Test handling of non-existent file."""
    print("\nTesting non-existent file handling...")
    convertor = DataConvertor()
    
    try:
        convertor.convert('nonexistent.xlsx')
        print("✗ Non-existent file validation failed")
    except DataConvertorError as e:
        print(f"✓ Non-existent file correctly caught: {e}")

def create_test_json():
    """Create test JSON files with valid data."""
    # Create test data - list format
    data_list = [
        {'id': '001', 'name': 'Item A', 'weight': 1.5, 'cost': 100, 'priority': 3},
        {'id': '002', 'name': 'Item B', 'weight': 2.3, 'cost': 150, 'priority': 1},
        {'id': '003', 'name': 'Item C', 'weight': 0.8, 'cost': 80, 'priority': 2},
        {'id': '004', 'name': 'Item D', 'weight': 3.1, 'cost': 200, 'priority': 1}
    ]
    
    # Save list format
    list_file = Path('test_data_list.json')
    with open(list_file, 'w') as f:
        json.dump(data_list, f, indent=2)
    
    # Create dict format with 'data' key
    data_dict = {'data': data_list}
    dict_file = Path('test_data_dict.json')
    with open(dict_file, 'w') as f:
        json.dump(data_dict, f, indent=2)
    
    return list_file, dict_file

def create_invalid_json():
    """Create test JSON files with invalid data."""
    # Missing ID
    data_no_id = [
        {'name': 'Item A', 'weight': 1.5},
        {'name': 'Item B', 'weight': 2.3}
    ]
    no_id_file = Path('test_json_no_id.json')
    with open(no_id_file, 'w') as f:
        json.dump(data_no_id, f)
    
    # Duplicate IDs
    data_dup_id = [
        {'id': '001', 'name': 'Item A'},
        {'id': '001', 'name': 'Item B'}
    ]
    dup_id_file = Path('test_json_dup_id.json')
    with open(dup_id_file, 'w') as f:
        json.dump(data_dup_id, f)
    
    # Invalid format (not list or dict)
    invalid_format_file = Path('test_json_invalid.json')
    with open(invalid_format_file, 'w') as f:
        json.dump("invalid string data", f)
    
    return no_id_file, dup_id_file, invalid_format_file

def test_json_conversion():
    """Test conversion of JSON data."""
    print("\nTesting JSON conversion...")
    list_file, dict_file = create_test_json()
    
    convertor = DataConvertor()
    
    try:
        # Test list format
        print("  Testing JSON list format...")
        result_list = convertor.convert(list_file)
        print("  ✓ List format conversion successful!")
        print(f"    - Unit attributes: {result_list.unit_attr}")
        print(f"    - Number of units: {len(result_list.units)}")
        
        # Test dict format
        print("  Testing JSON dict format...")
        result_dict = convertor.convert(dict_file)
        print("  ✓ Dict format conversion successful!")
        
        # Verify both formats produce same result
        assert len(result_list.units) == len(result_dict.units), "Different number of units"
        assert set(result_list.unit_attr) == set(result_dict.unit_attr), "Different attributes"
        print("  ✓ Both JSON formats produce consistent results!")
        
    finally:
        # Clean up
        list_file.unlink(missing_ok=True)
        dict_file.unlink(missing_ok=True)

def test_invalid_json():
    """Test handling of invalid JSON data."""
    print("\nTesting invalid JSON conversions...")
    no_id_file, dup_id_file, invalid_format_file = create_invalid_json()
    
    convertor = DataConvertor()
    
    # Test missing ID
    try:
        convertor.convert(no_id_file)
        print("  ✗ Missing ID validation failed")
    except DataConvertorError as e:
        print(f"  ✓ Missing ID correctly caught: {e}")
    finally:
        no_id_file.unlink(missing_ok=True)
    
    # Test duplicate IDs
    try:
        convertor.convert(dup_id_file)
        print("  ✗ Duplicate ID validation failed")
    except DataConvertorError as e:
        print(f"  ✓ Duplicate ID correctly caught: {e}")
    finally:
        dup_id_file.unlink(missing_ok=True)
    
    # Test invalid format
    try:
        convertor.convert(invalid_format_file)
        print("  ✗ Invalid format validation failed")
    except DataConvertorError as e:
        print(f"  ✓ Invalid format correctly caught: {e}")
    finally:
        invalid_format_file.unlink(missing_ok=True)

def test_extensibility():
    """Test the extensibility of DataConvertor."""
    print("\nTesting extensibility...")
    
    # Test unsupported format
    convertor = DataConvertor()
    try:
        convertor.convert('test.csv')  # Changed to CSV since JSON is now supported
        print("✗ Unsupported format validation failed")
    except DataConvertorError as e:
        print(f"✓ Unsupported format correctly caught: {e}")
    
    # Show supported formats
    print(f"  Supported formats: {list(convertor._convertors.keys())}")

def main():
    """Run all tests."""
    print("=== DataConvertor Test Suite ===\n")
    
    try:
        # Excel tests
        test_valid_conversion()
        test_invalid_conversions()
        test_nonexistent_file()
        
        # JSON tests
        test_json_conversion()
        test_invalid_json()
        
        # General tests
        test_extensibility()
        
        print("\n=== All tests completed successfully! ===")
        
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
