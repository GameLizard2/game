import unittest
from unittest.mock import patch
from io import StringIO
import sys
import re
from typing import List, Tuple, Dict
import difflib

class GameTestCase:
    def __init__(self, name: str, inputs: List[str], expected_outputs: List[str], description: str = ""):
        self.name = name
        self.inputs = inputs
        self.expected_outputs = expected_outputs
        self.description = description

class DeepSpaceTestFramework(unittest.TestCase):
    def setUp(self):
        self.held_output = StringIO()
        self.actual_output = []
        self.original_stdout = sys.stdout
        sys.stdout = self.held_output

    def tearDown(self):
        sys.stdout = self.original_stdout
        self.held_output.close()

    def _normalize_output(self, output: str) -> str:
        """����������� ����� ��� ���������, ������ ������� � ������� � ������� ��������"""
        return re.sub(r'\s+', ' ', output.lower().strip())

    def _compare_outputs(self, actual: List[str], expected: List[str]) -> Tuple[bool, str]:
        """���������� ����������� � ��������� �����, ��������� ��������� � diff"""
        actual_norm = [self._normalize_output(line) for line in actual if line.strip()]
        expected_norm = [self._normalize_output(line) for line in expected if line.strip()]
        
        diff = list(difflib.unified_diff(
            expected_norm,
            actual_norm,
            fromfile='expected',
            tofile='actual',
            lineterm=''
        ))
        
        return len(diff) == 0, '\n'.join(diff)

    def run_test_case(self, test_case: GameTestCase) -> Dict:
        """��������� �������� �������� � ���������� ����������"""
        input_generator = (input_value for input_value in test_case.inputs)
        
        with patch('builtins.input', lambda _: next(input_generator)):
            try:
                import console_game
                console_game.game_intro()
            except Exception as e:
                return {
                    'name': test_case.name,
                    'description': test_case.description,
                    'status': 'ERROR',
                    'error': str(e),
                    'diff': None
                }

        actual_output = self.held_output.getvalue().split('\n')
        is_match, diff = self._compare_outputs(actual_output, test_case.expected_outputs)
        
        return {
            'name': test_case.name,
            'description': test_case.description,
            'status': 'PASS' if is_match else 'FAIL',
            'error': None,
            'diff': diff if not is_match else None
        }

# ����������� ����� �������� ���������
TEST_CASES = [
    GameTestCase(
        name="Basic Scout Ship Selection",
        description="�������� �������� ������ ������� Scout � ��� �������������",
        inputs=["1"],  # ����� Scout
        expected_outputs=[
            "DEEPSPACE",
            "CREATIVE COMPUTING",
            "MORRISTOWN, NEW JERSEY",
            "THIS IS DEEPSPACE, A TACTICAL SIMULATION OF SHIP TO SHIP COMBAT IN DEEP SPACE.",
            "Ships have the following characteristics:",
            "TYPE        SPEED   CARGO SPACE   PROTECTION",
            "1. SCOUT     10X        16            1",
            "You selected the SCOUT."
        ]
    ),
    
    GameTestCase(
        name="Full Cruiser Combat Setup",
        description="������ ��������� �������� � ������������ �����������",
        inputs=[
            "2",  # ����� Cruiser
            "1",  # Phaser Banks
            "2",  # Anti-Matter Missile
            "3",  # Hyperspace Lance
            "4",  # Photon Torpedo
            "5"   # ���������� ������
        ],
        expected_outputs=[
            "You selected the CRUISER.",
            "Now, select your weapons",
            "You have chosen Phaser Banks",
            "You have chosen Anti-Matter Missile",
            "You have chosen Hyperspace Lance",
            "You have chosen Photon Torpedo",
            "Cargo space is full or weapon selection finished. Prepare for battle!"
        ]
    ),
    
    GameTestCase(
        name="Battleship Maximum Weapons",
        description="�������� �������� ������������� ���������� ������ �� ������",
        inputs=[
            "3",  # ����� Battleship
            "1",  # Phaser Banks
            "2",  # Anti-Matter Missile
            "2",  # ��� Anti-Matter Missile
            "3",  # Hyperspace Lance
            "4",  # Photon Torpedo
            "4",  # ��� Photon Torpedo
            "5"   # ���������� ������
        ],
        expected_outputs=[
            "You selected the BATTLESHIP.",
            "Now, select your weapons",
            "=== BATTLE INITIATED ==="
        ]
    ),
    
    GameTestCase(
        name="Invalid Ship Selection",
        description="�������� ��������� ��������� ������ �������",
        inputs=[
            "4",  # �������� �����
            "0",  # ��� �������� �����
            "1"   # ���������� �����
        ],
        expected_outputs=[
            "Invalid choice. Please select 1, 2, or 3.",
            "You selected the SCOUT."
        ]
    ),
    
    GameTestCase(
        name="Cargo Space Overflow Test",
        description="�������� ������������ ��������� ������",
        inputs=[
            "1",  # ����� Scout (16 cargo space)
            "1",  # Phaser Banks (12 space)
            "2",  # Anti-Matter Missile (4 space)
            "2",  # ������� �������� ��� Anti-Matter Missile
            "5"   # ���������� ������
        ],
        expected_outputs=[
            "You selected the SCOUT.",
            "Not enough cargo space",
            "Cargo space is full or weapon selection finished"
        ]
    ),
    
    GameTestCase(
        name="Duplicate Weapon Selection",
        description="�������� ������� �� ������������ ������",
        inputs=[
            "2",  # ����� Cruiser
            "1",  # Phaser Banks
            "1",  # ������� ������� Phaser Banks �����
            "5"   # ���������� ������
        ],
        expected_outputs=[
            "You already have Phaser Banks in your loadout",
            "Choose another weapon"
        ]
    ),
    
    GameTestCase(
        name="Full Combat Scenario",
        description="������ �������� ��� � �������������� ���� ����� ������",
        inputs=[
            "2",  # ����� Cruiser
            "1",  # Phaser Banks
            "2",  # Anti-Matter Missile
            "4",  # Photon Torpedo
            "5"   # ���������� ������
        ],
        expected_outputs=[
            "You selected the CRUISER.",
            "=== BATTLE INITIATED ===",
            "You are now engaging Alien Destroyer in battle!",
            "Your ship is equipped with the following loadout:"
        ]
    ),
    
    GameTestCase(
        name="Minimal Scout Setup",
        description="����������� ������������ ���������� � ����� ����� ������",
        inputs=[
            "1",  # ����� Scout
            "4",  # ������ Photon Torpedo
            "5"   # ���������� ������
        ],
        expected_outputs=[
            "You selected the SCOUT.",
            "You have chosen Photon Torpedo",
            "=== BATTLE INITIATED ==="
        ]
    ),
    
    GameTestCase(
        name="Maximum Battleship Protection",
        description="�������� ������������ ������ �������",
        inputs=[
            "3",  # ����� Battleship
            "1",  # Phaser Banks
            "5"   # ���������� ������
        ],
        expected_outputs=[
            "You selected the BATTLESHIP.",
            "protection: 5",
            "=== BATTLE INITIATED ==="
        ]
    )
]

def run_all_tests():
    """��������� ��� �������� �������� � ������� ����������"""
    test_framework = DeepSpaceTestFramework()
    results = []
    
    print("=== Starting DeepSpace Game Tests ===\n")
    
    for test_case in TEST_CASES:
        print(f"Running test: {test_case.name}")
        print(f"Description: {test_case.description}")
        
        test_framework.setUp()
        result = test_framework.run_test_case(test_case)
        results.append(result)
        test_framework.tearDown()
        
        print(f"Status: {result['status']}")
        if result['error']:
            print(f"Error: {result['error']}")
        if result['diff']:
            print("\nDifferences found:")
            print(result['diff'])
        print("\n" + "="*50 + "\n")
    
    # �������� ����������
    total_tests = len(results)
    passed_tests = sum(1 for r in results if r['status'] == 'PASS')
    failed_tests = sum(1 for r in results if r['status'] == 'FAIL')
    error_tests = sum(1 for r in results if r['status'] == 'ERROR')
    
    print("\n=== Test Summary ===")
    print(f"Total tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")
    print(f"Errors: {error_tests}")
    print(f"Success rate: {(passed_tests/total_tests)*100:.2f}%")

if __name__ == '__main__':
    run_all_tests()
    