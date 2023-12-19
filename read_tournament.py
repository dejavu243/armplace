"""
Read tournament from files

1. Вычитываем N спортсменов из файла *_[DE].txt (спортсмены указаны в порядке после жеребьевки);
2. Вычитываем результаты поединков Res (последняя строка в файле *_[DE].txt);
3. Вычитываем веса спортсменов из файла *_[ADE].txt (для файла спортсменов из *_[DE].txt)
4. Если длина слова Res с результатами поединков M=2*(N-1), то в категории нет суперфинала, если M=2*(N-1)+1,
то в категории был суперфинал. Длина слова M будет использоваться в дальнейшем;
5. Задаем генеральную последовательность (линейный массив GS) длины (2*M+N);
6. Записываем номера спортсменов (помним соответствие между номером и именем) в генеральную последовательность
с 1-го элемента;
7. Запускаем цикл по GS, двигаясь по парам, т.е. с шагом в 2 элемента последовательности (i – номер итерации / пары).
Если в i-й ячейке Res записан ‘+’, то номер первого из пары перемещается в ячейку GS c номером DE_OLD_Winner[i][N+1],
а проигравшего в DE_OLD_Loser[i][N+1], если ‘-’, то наоборот. Проходим все пары  до i = M.
В процессе формируем массив пар для построения графа без перестановки порядка в паре, если ‘+’
и с перестановкой порядка, если ‘-’. Если в Res записан ‘>’, то пара в массив для графа не записывается,
так как это техническая победа, но перемещение в GS равносильно ‘+’, аналогично для ‘<’ и ‘-’;
8. В процессе движения записываем следующие параметры для каждого спортсмена: кол-во побед Win; номер того,
кто победил спортсмена Num_Los;9. Вычитываем пару поединка за 5-6 места из *_[DE_5-6].txt и Res_5-6, из которого
нужен только первый символ. Согласно ‘+’ или ‘–‘ записываем пару в массив для построения графа;
10. Если требуется, то вычитываем веса спортсменов, участвующих в поединке за 5-6 места из _[DE_0_5-6].txt;
"""

import logging
from glob import glob
from pathlib import Path
from typing import Union

from data.DE_OLD_Loser import DE_OLD_loser
from data.DE_OLD_Winner import DE_OLD_winner

logger = logging.getLogger(__name__)
logging.basicConfig()
logger.setLevel(logging.INFO)

RESULT_FILE_SUFFIX = "[DE]"
RESULT_FILE_5_6_SUFFIX = "[DE_5-6]"
WEIGHTS_FILE_SUFFIX = "[ADE]"
WEIGHTS_FILE_5_6_SUFFIX = "[DE_0_5-6]"

CURRENT_DIR = Path(__file__).parent.resolve()


def read_names(lines: list) -> tuple:
    names = {}
    results = None
    for i, name in enumerate(lines):
        if "+" not in name and "-" not in name:
            names[i + 1] = name.strip()
        else:
            results = list(name.strip())
    return names, results


def read_weigths(lines: list) -> dict:
    weights = {}
    for i, weight in enumerate(lines):
        weights[i + 1] = float(weight.strip().replace(",", "."))
    return weights


def read_tournament_files(filepath: Union[Path, str]) -> dict:
    filelist = glob(filepath + "*.txt")
    logger.info("filelist: %s", filelist)
    _files = {RESULT_FILE_SUFFIX: None, RESULT_FILE_5_6_SUFFIX: None,
              WEIGHTS_FILE_SUFFIX: None, WEIGHTS_FILE_5_6_SUFFIX: None}
    for filename in filelist:
        try:
            file = open(filename, "r", encoding="utf-8")
            lines = file.readlines()
            if RESULT_FILE_SUFFIX in filename:
                names, results = read_names(lines)
                _files[RESULT_FILE_SUFFIX] = [names, results]
                logger.debug(f"{names=}")
                logger.debug(f"{results=}")
            elif WEIGHTS_FILE_SUFFIX in filename:
                weights = read_weigths(lines)
                _files[WEIGHTS_FILE_SUFFIX] = weights
                logger.debug(f"{weights=}")
            elif RESULT_FILE_5_6_SUFFIX in filename:
                names, results = read_names(lines)
                _files[RESULT_FILE_5_6_SUFFIX] = [names, results]
                logger.debug(f"{names=}")
                logger.debug(f"{results=}")
            elif WEIGHTS_FILE_5_6_SUFFIX in filename:
                weights = read_weigths(lines)
                _files[WEIGHTS_FILE_5_6_SUFFIX] = weights
                logger.debug(f"{weights=}")
            else:
                logger.warning("File %s not mathing with tournament files", filename)
        except Exception as error:
            logger.error("File %s doesn't read, check existence or encoding \n%s", filename, error)
    logger.info(f"{len(_files.keys())} tournament files read")
    return _files


def drop_simple_cycles(_pairs: list) -> list:
    pairs_without_simple_cycles = []
    for _pair in _pairs:
        pair_forward_count = _pairs.count(_pair)
        pair_backward_count = _pairs.count((_pair[1], _pair[0]))
        logger.debug(f"{_pair=}, {pair_forward_count=}, {pair_backward_count=}")
        if pair_forward_count >= 1 and pair_backward_count == 0:
            if _pair not in pairs_without_simple_cycles:
                pairs_without_simple_cycles.append(_pair)
        if pair_forward_count == 2 and pair_backward_count == 1:
            if (_pair[1], _pair[0]) not in pairs_without_simple_cycles:
                pairs_without_simple_cycles.append(_pair)
        if pair_forward_count == 1 and pair_backward_count == 2:
            if _pair not in pairs_without_simple_cycles:
                pairs_without_simple_cycles.append((_pair[1], _pair[0]))

    if len(_pairs) != len(pairs_without_simple_cycles):
        logger.info(f"Dropped pairs number: {len(_pairs) - len(pairs_without_simple_cycles)}, "
                    f"number of result pairs: {len(pairs_without_simple_cycles)}")

    return pairs_without_simple_cycles


def tournament_recovery(_files: dict) -> list:
    names, results = _files[RESULT_FILE_SUFFIX]
    sportsmen_count = len(names.keys())
    result_length = len(results)
    sequence_length = 2 * (result_length + 1) + sportsmen_count
    with_superfinal = True if result_length == 2 * (sportsmen_count - 1) + 1 else False
    tournament_sequence = [0] * sequence_length
    logger.debug(f"{sequence_length=}, {result_length=}, {sportsmen_count=}, {with_superfinal=}")
    for index, name in names.items():
        tournament_sequence[index - 1] = index
    _pairs = []
    pair_counter = 0

    for index in range(0, len(tournament_sequence), 2):
        pair_index = index // 2
        pair_counter += 1
        logger.debug(f"{index=}, {pair_index=}, {pair_counter=}")

        if pair_index == result_length:
            logger.debug(f"pair_index == result_length {index=} {pair_index=}")
            break

        if results[pair_index] == "+":
            winner_index_in_names = tournament_sequence[index]
            loser_index_in_names = tournament_sequence[index + 1]
            new_winner_index = DE_OLD_winner[pair_index][sportsmen_count - 2]  # TODO: why -2
            new_loser_index = DE_OLD_loser[pair_index][sportsmen_count - 2]
            logger.debug(
                f"{loser_index_in_names=}, {winner_index_in_names=}, {new_loser_index=}, {new_winner_index=} {results[pair_index]=}")

            tournament_sequence[new_winner_index - 1] = winner_index_in_names
            tournament_sequence[new_loser_index - 1] = loser_index_in_names
            logger.debug(
                f"pair: {names[winner_index_in_names]} (win), {names[loser_index_in_names]} (loose)")
            # _pairs.append((names[winner_index_in_names], names[loser_index_in_names]))
            _pairs.append((names[loser_index_in_names], names[winner_index_in_names]))

        elif results[pair_index] == "-":
            winner_index_in_names = tournament_sequence[index + 1]
            loser_index_in_names = tournament_sequence[index]
            new_winner_index = DE_OLD_winner[pair_index][sportsmen_count - 2]
            new_loser_index = DE_OLD_loser[pair_index][sportsmen_count - 2]
            logger.debug(
                f"{loser_index_in_names=}, {winner_index_in_names=}, {new_loser_index=}, {new_winner_index=} {results[pair_index]=}")

            tournament_sequence[new_winner_index - 1] = winner_index_in_names
            tournament_sequence[new_loser_index - 1] = loser_index_in_names
            logger.debug(
                f"pair {names[winner_index_in_names]} (win), {names[loser_index_in_names]} (loose)")
            # _pairs.append((names[winner_index_in_names], names[loser_index_in_names]))
            _pairs.append((names[loser_index_in_names], names[winner_index_in_names]))

    # добавление пары за 5-6 место
    if _files[RESULT_FILE_5_6_SUFFIX]:
        names, results = _files[RESULT_FILE_5_6_SUFFIX]
        pair_counter += 1
        if results[0] == "+":
            _pairs.append((names[1], names[2]))
        elif results[0] == "-":
            _pairs.append((names[2], names[1]))

    logger.info(f"Pairs number: {len(_pairs)}")
    logger.debug(tournament_sequence)

    return drop_simple_cycles(_pairs)


##########If run from here###########
if __name__ == '__main__':
    files = read_tournament_files('./data/left_hand_75kg/')
    pairs = tournament_recovery(files)

    for pair in pairs:
        print(pair)
