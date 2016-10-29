#coding=utf-8

__author__ = 'karldoenitz'

def convert_merged_cells(merged_cells):
    conver_cells = []
    for need_cell in merged_cells:
        cl = need_cell.split(':')

def convert_string_to_number(st):
    l = list(st)
    num = 0
    for character in l:
        num = num * 26 + (ord(character) - 64)
    return num


def get_number_from_string(st):
    l = list(st)
    j = 0
    for i in range(len(l)):
        if ord(l[i]) >= ord('0') and ord(l[i]) <= ord('9'):
            j = i
            break
    l = []
    l.append(st[0:j])
    l.append(st[j:len(st)])
    return l


def convert_merged_cells(merged_cells):
    converted_merged_cells = []
    for cells in merged_cells:
        new_list = cells.split(":")
        l = []
        l1 = get_number_from_string(new_list[0])
        l2 = get_number_from_string(new_list[1])
        l.append(int(l1[1])-1)
        l.append(int(l2[1]))
        l.append(convert_string_to_number(l1[0])-1)
        l.append(convert_string_to_number(l2[0]))
        converted_merged_cells.append(tuple(l))
    return converted_merged_cells