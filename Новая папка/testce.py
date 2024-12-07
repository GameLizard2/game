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
    @classmethod
    def setUpClass(cls):
        if 'console_game' in sys.modules:
            del sys.modules['console_game']

    def setUp(self):
        self.held_output = StringIO()
        self.original_stdout = sys.stdout
        sys.stdout = self.held_output

    def tearDown(self):
        sys.stdout = self.original_stdout
        self.held_output.close()

    def _normalize_output(self, output: str) -> str:
        """Нормализует вывод для сравнения, удаляя пробелы и приводя к нижнему регистру"""
        return re.sub(r'\s+', ' ', output.lower().strip())

    def _filter_battle_output(self, lines: List[str]) -> List[str]:
        """Фильтрует вывод боевой части"""
        filtered = []
        for line in lines:
            if "=== BATTLE INITIATED ===" in line.upper():
                break
            filtered.append(line)
        return filtered

    def _compare_outputs(self, actual: List[str], expected: List[str]) -> Tuple[bool, str]:
        """Сравнивает фактический и ожидаемый вывод, возвращая результат и diff"""
        # Фильтруем вывод боя
        actual_filtered = self._filter_battle_output(actual)

        actual_norm = [self._normalize_output(line) for line in actual_filtered if line.strip()]
        expected_norm = [self._normalize_output(line) for line in expected if line.strip()]

        print("\nNormalized Expected output:")
        for line in expected_norm:
            print(f"  {line}")

        print("\nNormalized Actual output:")
        for line in actual_norm:
            print(f"  {line}")

        diff = list(difflib.unified_diff(
            expected_norm,
            actual_norm,
            fromfile='expected',
            tofile='actual',
            lineterm=''
        ))

        return len(diff) == 0, '\n'.join(diff)

    def run_test_case(self, test_case: GameTestCase) -> Dict:
        """Запускает тестовый сценарий и возвращает результаты"""
        try:
            with patch('builtins.input', side_effect=test_case.inputs), \
                    patch('console_game.battle_cycle', return_value=None), \
                    patch('console_game.start_battle', return_value=None):

                import console_game

                # Сбрасываем состояние игры
                console_game.ship_stats = {'speed': 0, 'cargo_space': 0, 'protection': 0}
                console_game.cargo_used = 0
                console_game.loadout = []

                console_game.game_intro()

            # Получаем вывод и обрезаем его на фразе о подготовке к бою
            output = self.held_output.getvalue()
            output_lines = output.split('\n')
            filtered_lines = []
            for line in output_lines:
                filtered_lines.append(line)
                if "Prepare for battle!" in line:
                    break

            # Сравниваем только отфильтрованный вывод
            is_match, diff = self._compare_outputs(filtered_lines, test_case.expected_outputs)

            return {
                'name': test_case.name,
                'description': test_case.description,
                'status': 'PASS' if is_match else 'FAIL',
                'error': None,
                'diff': diff if not is_match else None,
                'output': '\n'.join(filtered_lines)
            }

        except Exception as e:
            import traceback
            return {
                'name': test_case.name,
                'description': test_case.description,
                'status': 'ERROR',
                'error': f"Error during test execution: {str(e)}\n{traceback.format_exc()}",
                'diff': None,
                'output': ''
            }


def run_all_tests():
    """Запускает все тестовые сценарии и выводит результаты"""
    if not TEST_CASES:
        print("No test cases defined!")
        return

    test_framework = DeepSpaceTestFramework()
    results = []

    print("\n" + "=" * 80)
    print("=== Starting DeepSpace Game Tests ===".center(80))
    print("=" * 80 + "\n")

    total_time_start = time.time()

    for test_case in TEST_CASES:
        print("=" * 80)
        print(f"Test Case: {test_case.name}")
        print(f"Description: {test_case.description}")
        print("-" * 80)
        print(f"Input sequence: {test_case.inputs}")
        print("-" * 80)

        test_start_time = time.time()

        test_framework.setUp()
        result = test_framework.run_test_case(test_case)
        results.append(result)
        test_framework.tearDown()

        test_end_time = time.time()
        test_duration = test_end_time - test_start_time

        print(f"\nTest Status: {result['status']}")
        print(f"Test Duration: {test_duration:.3f} seconds")

        if result['error']:
            print("\nError Details:")
            print("-" * 40)
            print(result['error'])

        if result['diff']:
            print("\nOutput Differences:")
            print("-" * 40)
            print(result['diff'])

        print("\nTest Output Preview:")
        print("-" * 40)
        output_lines = result['output'].split('\n')
        preview_lines = 5

        if len(output_lines) > preview_lines * 2:
            print(f"\nFirst {preview_lines} lines of output:")
            for line in output_lines[:preview_lines]:
                print(f"  {line}")
            print("  ...")
            print(f"\nLast {preview_lines} lines of output:")
            for line in output_lines[-preview_lines:]:
                print(f"  {line}")
        else:
            print("\nComplete output:")
            for line in output_lines:
                print(f"  {line}")
        print("\n" + "=" * 80 + "\n")
    total_time_end = time.time()
    total_duration = total_time_end - total_time_start

    # Итоговая статистика
    total_tests = len(results)
    passed_tests = sum(1 for r in results if r['status'] == 'PASS')
    failed_tests = sum(1 for r in results if r['status'] == 'FAIL')
    error_tests = sum(1 for r in results if r['status'] == 'ERROR')

    print("\n" + "=" * 80)
    print("=== Test Summary ===".center(80))
    print("=" * 80)
    print(f"\nTotal Tests Run: {total_tests}")
    print(f"Tests Passed:    {passed_tests:3d} ({(passed_tests / total_tests) * 100:.1f}%)")
    print(f"Tests Failed:    {failed_tests:3d} ({(failed_tests / total_tests) * 100:.1f}%)")
    print(f"Tests Errored:   {error_tests:3d} ({(error_tests / total_tests) * 100:.1f}%)")
    print(f"\nTotal Test Duration: {total_duration:.3f} seconds")
    print("\nTest Results Breakdown:")
    print("-" * 40)

    for i, result in enumerate(results, 1):
        status_color = {
            'PASS': '\033[92m',  # Зеленый
            'FAIL': '\033[91m',  # Красный
            'ERROR': '\033[93m'  # Желтый
        }.get(result['status'], '')
        reset_color = '\033[0m'

        print(f"{i:2d}. {result['name']:<30} - {status_color}{result['status']}{reset_color}")

    print("\n" + "=" * 80)

    success_color = '\033[92m' if passed_tests == total_tests else '\033[91m'
    print(f"\nFinal Success Rate: {success_color}{(passed_tests / total_tests) * 100:.2f}%{reset_color}")
    print("\n" + "=" * 80)


# Тестовые случаи
# Добавим следующие тестовые случаи:

# -*- coding: utf-8 -*-

TEST_CASES = [
    GameTestCase(
        name="Full Game With Instructions",
        description="Полный диалог игры с просмотром инструкций",
        inputs=[
            "YES",  # Do you wish instructions?
            "YES",  # Do you wish a manuever chart?
            "1",  # Select Orion system
            "1",  # Select Scout
            "1",  # Choose Phaser Banks
            "1",  # Amount: 1
            "5"  # Done selecting weapons
        ],
        expected_outputs=[
            "                            DEEPSPACE",
            "                        CREATIVE COMPUTING",
            "                      MORRISTOWN, NEW JERSEY",
            "",
            "",
            "",
            "THIS IS DEEPSPACE, A TACTICAL SIMULATION OF SHIP TO SHIP",
            "COMBAT IN DEEP SPACE",
            "DO YOU WISH INSTRUCTIONS?",
            "YOU ARE ONE OF A GROUP OF CAPTAINS ASSIGNED TO PATROL A",
            "SECTION OF YOUR STAR EMPIRE'S BORDER AGAINST HOSTILE",
            "ALIENS ALL YOUR ENCOUNTERS HERE WILL BE AGAINST HOSTILE",
            "VESSELS YOU WILL FIRST BE REQUIRED TO SELECT A VESSEL",
            "FROM ONE OF THREE TYPES, EACH WITH ITS OWN CHARACTERISTICS",
            "",
            "TYPE",
            "SPEED",
            "CARGO SPACE",
            "PROTECTION",
            "1 SCOUT",
            "10X",
            "16",
            "1",
            "2 CRUISER",
            "4X",
            "24",
            "2",
            "3 BATTLESHIP",
            "2X",
            "30",
            "5",
            "",
            "SPEED IS GIVEN RELATIVE TO THE OTHER SHIPS",
            "CARGO SPACE IS IN UNITS OF SPACE ABOARD SHIP WHICH CAN BE",
            "FILLED WITH WEAPONS",
            "PROTECTION IS THE RELATIVE STRENGTH OF THE SHIP'S ARMOR",
            "AND FORCE FIELDS",
            "",
            "DO YOU WISH A MANUEVER CHART?",
            "     **************",
            "     MANUEVER CHART",
            "",
            " 1      FIRE PHASERS",
            " 2      FIRE ANTI-MATTER MISSILE",
            " 3      FIRE HYPERSPACE LANCE",
            " 4      FIRE PHOTON TORPEDO",
            " 5      ACTIVE HYPERON NEUTRALIZATION FIELD",
            " 6      SELF-DESTRUCT",
            " 7      CHANGE VELOCITY",
            " 8      DISENGAGE",
            " 9      PROCEED",
            "",
            "YOU HAVE A CHOICE OF THREE SYSTEMS TO PATROL",
            "1 ORION",
            "2 DENEB",
            "3 ARCTURUS",
            "SELECT A SYSTEM(1-3)?",
            "WHICH SPACECRAFT WOULD YOU LIKE(1-3)?",
            "1 SCOUT SELECTED",
            "YOU HAVE 16 UNITS OF CARGO SPACE TO FILL WITH WEAPONRY",
            "CHOOSE A WEAPON AND THE AMOUNT YOU WISH",
            "",
            "TYPE                         CARGO SPACE    REL. STRENGTH",
            "1 PHASER BANKS                   12                4",
            "2 ANTI-MATTER MISSILE             4               20",
            "3 HYPERSPACE LANCE                4               16",
            "4 PHOTON TORPEDO                  2               10",
            "5 DONE WITH SELECTION",
            "",
            "CHOOSE A WEAPON?",
            "HOW MANY?",
            "REMAINING CARGO SPACE: 4",
            "",
            "TYPE                         CARGO SPACE    REL. STRENGTH",
            "1 PHASER BANKS                   12                4",
            "2 ANTI-MATTER MISSILE             4               20",
            "3 HYPERSPACE LANCE                4               16",
            "4 PHOTON TORPEDO                  2               10",
            "5 DONE WITH SELECTION",
            "",
            "CHOOSE A WEAPON?",
            "WEAPON SELECTION COMPLETE"
        ]
    ),

    GameTestCase(
        name="Different System Choice",
        description="Проверка выбора системы Deneb",
        inputs=[
            "NO",     # Do you wish instructions?
            "NO",     # Do you wish a manuever chart?
            "2",      # Select Deneb system
            "1",      # Select Scout
            "5"       # Done selecting weapons
        ],
        expected_outputs=[
            "                            DEEPSPACE",
            "                        CREATIVE COMPUTING",
            "                      MORRISTOWN, NEW JERSEY",
            "",
            "",
            "",
            "THIS IS DEEPSPACE, A TACTICAL SIMULATION OF SHIP TO SHIP",
            "COMBAT IN DEEP SPACE",
            "DO YOU WISH INSTRUCTIONS?",
            "DO YOU WISH A MANUEVER CHART?",
            "",
            "YOU HAVE A CHOICE OF THREE SYSTEMS TO PATROL",
            "1 ORION",
            "2 DENEB",
            "3 ARCTURUS",
            "SELECT A SYSTEM(1-3)?",
            "WHICH SPACECRAFT WOULD YOU LIKE(1-3)?",
            "1 SCOUT SELECTED",
            "YOU HAVE 16 UNITS OF CARGO SPACE TO FILL WITH WEAPONRY",
            "CHOOSE A WEAPON AND THE AMOUNT YOU WISH",
            "",
            "TYPE                         CARGO SPACE    REL. STRENGTH",
            "1 PHASER BANKS                   12                4",
            "2 ANTI-MATTER MISSILE             4               20",
            "3 HYPERSPACE LANCE                4               16",
            "4 PHOTON TORPEDO                  2               10",
            "5 DONE WITH SELECTION",
            "",
            "CHOOSE A WEAPON?",
            "WEAPON SELECTION COMPLETE"
        ]
    ),

    GameTestCase(
        name="Invalid Inputs Handling",
        description="Проверка обработки неверных вводов",
        inputs=[
            "NO",     # Do you wish instructions?
            "NO",     # Do you wish a manuever chart?
            "4",      # Invalid system choice
            "1",      # Correct system choice
            "5",      # Invalid ship choice
            "1",      # Correct ship choice (Scout)
            "1",      # Choose Phaser Banks
            "1",      # Amount: 1
            "6",      # Invalid weapon choice
            "5"       # Done selecting weapons
        ],
        expected_outputs=[
            "                            DEEPSPACE",
            "                        CREATIVE COMPUTING",
            "                      MORRISTOWN, NEW JERSEY",
            "",
            "",
            "",
            "THIS IS DEEPSPACE, A TACTICAL SIMULATION OF SHIP TO SHIP",
            "COMBAT IN DEEP SPACE",
            "DO YOU WISH INSTRUCTIONS?",
            "DO YOU WISH A MANUEVER CHART?",
            "",
            "YOU HAVE A CHOICE OF THREE SYSTEMS TO PATROL",
            "1 ORION",
            "2 DENEB",
            "3 ARCTURUS",
            "SELECT A SYSTEM(1-3)?",
            "INVALID CHOICE",
            "SELECT A SYSTEM(1-3)?",
            "WHICH SPACECRAFT WOULD YOU LIKE(1-3)?",
            "INVALID CHOICE",
            "WHICH SPACECRAFT WOULD YOU LIKE(1-3)?",
            "1 SCOUT SELECTED",
            "YOU HAVE 16 UNITS OF CARGO SPACE TO FILL WITH WEAPONRY",
            "CHOOSE A WEAPON AND THE AMOUNT YOU WISH",
            "",
            "TYPE                         CARGO SPACE    REL. STRENGTH",
            "1 PHASER BANKS                   12                4",
            "2 ANTI-MATTER MISSILE             4               20",
            "3 HYPERSPACE LANCE                4               16",
            "4 PHOTON TORPEDO                  2               10",
            "5 DONE WITH SELECTION",
            "",
            "CHOOSE A WEAPON?",
            "HOW MANY?",
            "REMAINING CARGO SPACE: 4",
            "",
            "TYPE                         CARGO SPACE    REL. STRENGTH",
            "1 PHASER BANKS                   12                4",
            "2 ANTI-MATTER MISSILE             4               20",
            "3 HYPERSPACE LANCE                4               16",
            "4 PHOTON TORPEDO                  2               10",
            "5 DONE WITH SELECTION",
            "",
            "CHOOSE A WEAPON?",
            "INVALID CHOICE",
            "TYPE                         CARGO SPACE    REL. STRENGTH",
            "1 PHASER BANKS                   12                4",
            "2 ANTI-MATTER MISSILE             4               20",
            "3 HYPERSPACE LANCE                4               16",
            "4 PHOTON TORPEDO                  2               10",
            "5 DONE WITH SELECTION",
            "",
            "CHOOSE A WEAPON?",
            "WEAPON SELECTION COMPLETE"
        ]
    ),

    GameTestCase(
        name="Maximum Cargo Load Test",
        description="Проверка максимальной загрузки грузового отсека",
        inputs=[
            "NO",     # Do you wish instructions?
            "NO",     # Do you wish a manuever chart?
            "1",      # Select Orion
            "1",      # Select Scout (16 cargo space)
            "1",      # Choose Phaser Banks (12 space)
            "1",      # Amount: 1
            "2",      # Choose Anti-Matter Missile (4 space)
            "1",      # Amount: 1
            "5"       # Done selecting weapons
        ],
        expected_outputs=[
            "                            DEEPSPACE",
            "                        CREATIVE COMPUTING",
            "                      MORRISTOWN, NEW JERSEY",
            "",
            "",
            "",
            "THIS IS DEEPSPACE, A TACTICAL SIMULATION OF SHIP TO SHIP",
            "COMBAT IN DEEP SPACE",
            "DO YOU WISH INSTRUCTIONS?",
            "DO YOU WISH A MANUEVER CHART?",
            "",
            "YOU HAVE A CHOICE OF THREE SYSTEMS TO PATROL",
            "1 ORION",
            "2 DENEB",
            "3 ARCTURUS",
            "SELECT A SYSTEM(1-3)?",
            "WHICH SPACECRAFT WOULD YOU LIKE(1-3)?",
            "1 SCOUT SELECTED",
            "YOU HAVE 16 UNITS OF CARGO SPACE TO FILL WITH WEAPONRY",
            "CHOOSE A WEAPON AND THE AMOUNT YOU WISH",
            "",
            "TYPE                         CARGO SPACE    REL. STRENGTH",
            "1 PHASER BANKS                   12                4",
            "2 ANTI-MATTER MISSILE             4               20",
            "3 HYPERSPACE LANCE                4               16",
            "4 PHOTON TORPEDO                  2               10",
            "5 DONE WITH SELECTION",
            "",
            "CHOOSE A WEAPON?",
            "HOW MANY?",
            "REMAINING CARGO SPACE: 4",
            "",
            "TYPE                         CARGO SPACE    REL. STRENGTH",
            "1 PHASER BANKS                   12                4",
            "2 ANTI-MATTER MISSILE             4               20",
            "3 HYPERSPACE LANCE                4               16",
            "4 PHOTON TORPEDO                  2               10",
            "5 DONE WITH SELECTION",
            "",
            "CHOOSE A WEAPON?",
            "HOW MANY?",
            "REMAINING CARGO SPACE: 0",
            "CARGO SPACE IS FULL",
            "WEAPON SELECTION COMPLETE"
        ]
    )
]

if __name__ == '__main__':
    run_all_tests()
