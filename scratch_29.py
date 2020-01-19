import math
import os
import random

import numpy
import pygame


# Стандартная функция загрузки изображнения
def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    image = pygame.image.load(fullname)
    if colorkey is not None:

        if colorkey == -1:
            colorkey = image.get_at((0, 0))

        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()

    return image


# Главный игровой класс
class Board:
    def __init__(self, width, height, img_path):
        # перечисление существ и их характеристик
        self.creatures_pack = (('vadim', 8, 12, 10), ('peshka', 2, 3, 2), ('shield', 3, 16, 5), ('tank', 4, 24, 10))

        # Системные переменные
        self.screen = pygame.display.set_mode((width, height))
        self.my_bar = [0, 0, 0, 0, 0]
        self.opponent_bar = [0, 0, 0, 0, 0]
        self.my_hand = []
        self.take_card = False
        self.choose_opp = False
        self.clock = pygame.time.Clock()
        self.mouse_cor = []
        self.mana = 1
        self.i_took_card = -1
        self.cross = pygame.transform.scale(load_image('cross.png'), (145, 145))
        self._circle_cache = {}
        self.arrow_from = ()
        self.posi = []
        self.music_flag = True
        self.game_start = False
        self.loset_flag = False
        self.winner = False
        self.loser_sound_flag = False
        self.winner_sound_flag = False

        # гасим курсор
        pygame.mouse.set_visible(False)

        # Подгрузка ресурсов
        pygame.mixer_music.load('data/tricks-of-the-trade.mp3')
        pygame.mixer_music.play(10)
        self.loser_sound = pygame.mixer.Sound('data/loser.wav')
        self.winner_sound = pygame.mixer.Sound('data/winner.wav')
        self.kick = pygame.mixer.Sound('data/PUNCH.wav')
        self.kick.set_volume(0.3)
        self.your_turn_sound = pygame.mixer.Sound('data/your_turn .wav')
        self.cursor = load_image('JustHand.png')
        self.img = load_image(img_path)
        self.sound_button = load_image('sound.png')
        self.exit_button = load_image('exit.png')
        self.turn_button = load_image('turn_button_yellow.png')
        self.restart = load_image('restart.png')
        self.handdown = load_image('JustHandDown.png')
        self.handgrab = load_image('JustHandGrab.png')
        self.main_font = pygame.font.Font('data/main_font.ttf', 14)
        self.sec_font = pygame.font.Font('data/main_font.ttf', 16)

    # заполнение руки новыми случайными картами
    def hand_update(self):
        for i in range(6):

            a = random.choice(self.creatures_pack)

            if len(self.my_hand) < i + 1:
                self.my_hand.append(Creature(a[0], a[1], a[2], a[3]))

            else:
                self.my_hand[i] = Creature(a[0], a[1], a[2], a[3])

        for i in range(len(self.opponent_bar)):
            self.opponent_bar[i] = Creature_on_board('vadim', 8, 12, 10)

        for i in range(len(self.my_bar)):
            self.my_bar[i] = 0

    # общая отрисовка
    def allDraw(self, event):
        self.screen.fill((0, 0, 0))
        self.screen.blit(self.img, (0, 0))
        self.screen.blit(self.sound_button, (907, 511))
        self.screen.blit(self.exit_button, (907, 551))

        self.screen.blit(self.restart, (906, 440))

        if self.game_start and self.loset_flag is False and self.winner is False:
            self.my_bar_show()
            self.opponent_bar_draw()
            self.screen.blit(self.turn_button, (808, 319))
            if self.choose_opp and event.type != pygame.KEYDOWN:
                self.draw_arrow(self.screen, (100, 100, 100), (self.arrow_from[0], self.arrow_from[1]), event.pos)

            self.my_hand_show()

            if self.i_took_card != -1:
                self.screen.blit(self.i_took_card.img,
                                 (self.posi[0] - self.i_took_card.x, self.posi[1] - self.i_took_card.y))

            if event.type == pygame.MOUSEBUTTONDOWN and self.take_card is False:
                self.screen.blit(self.handdown, (self.posi[0] + 2, self.posi[1] + 1))

            elif pygame.mouse.get_focused() and self.choose_opp is False and self.take_card is False:
                self.screen.blit(self.cursor, self.posi)

            elif pygame.mouse.get_focused() and self.take_card is True:
                self.screen.blit(self.handgrab, self.posi)
        elif self.game_start is False and self.loset_flag is False:
            self.screen.blit(load_image('turn_button_grey.png'), (808, 319))
            text = self.render_text('Добро пожаловать в абсолютно уникальную и неповторимую игру KwantStone',
                                    self.sec_font)
            text1 = self.render_text('Для начала игры нажми эту прекрасную стрелку   --->', self.sec_font)
            self.screen.blit(text, (100, 200))
            self.screen.blit(text1, (300, 440))
        elif self.game_start and self.loset_flag:

            text = self.render_text('Ничего, у всех случаются осечки...  попробуй ещё!',
                                    self.sec_font)
            self.screen.blit(text, (250, 250))
        elif self.game_start and self.winner and self.loset_flag is False:

            text = self.render_text('победа!!!',
                                    self.sec_font)
            self.screen.blit(text, (480, 300))

    def opponent_bar_draw(self):
        for i in range(len(self.opponent_bar)):

            if self.opponent_bar[i] != 0:
                self.screen.blit(self.opponent_bar[i].img, (236 + 31 * i + 80 * i, 407 - 275))
                xp_text = self.render_text(str(self.opponent_bar[i].xp), self.main_font)
                at_text = self.render_text(str(self.opponent_bar[i].attack), self.main_font)
                x_xp = 62 if self.opponent_bar[i].xp // 10 != 0 else 65
                x_at = 3 if self.opponent_bar[i].attack // 10 != 0 else 5
                self.screen.blit(xp_text, (236 + 31 * i + 80 * i + x_xp, 407 + 88 - 275))
                self.screen.blit(at_text, (236 + 31 * i + 80 * i + x_at, 407 + 88 - 275))

                if self.opponent_bar[i].death_n != 0:

                    if self.opponent_bar[i].death_n == 60:
                        self.opponent_bar[i] = 0

                    else:
                        self.screen.blit(self.cross, (236 + 31 * i + 80 * i + x_xp - 15 - 80, 407 + 88 - 105 - 275))
                        self.opponent_bar[i].death_n += 1

    def new_turn(self):
        for i in self.my_bar:

            if i != 0:
                i.can_attack = True

    def make_cards_little_again(self):
        for i in self.my_hand:
            i.img = pygame.transform.scale(load_image(i.name + '.png'), (100, 160))
            i.hov_on = False

    def _circlepoints(self, r):
        r = int(round(r))

        if r in self._circle_cache:
            return self._circle_cache[r]

        x, y, e = r, 0, 1 - r
        self._circle_cache[r] = points = []

        while x >= y:
            points.append((x, y))
            y += 1
            if e < 0:
                e += 2 * y - 1

            else:
                x -= 1
                e += 2 * (y - x) - 1
        points += [(y, x) for x, y in points if x > y]
        points += [(-x, y) for x, y in points if x]
        points += [(x, -y) for x, y in points if y]
        points.sort()
        return points

    def my_bar_show(self):
        for i in range(len(self.my_bar)):

            if self.my_bar[i] != 0:
                self.screen.blit(self.my_bar[i].img, (236 + 31 * i + 80 * i, 407))
                xp_text = self.render_text(str(self.my_bar[i].xp), self.main_font)
                at_text = self.render_text(str(self.my_bar[i].attack), self.main_font)
                x_xp = 62 if self.my_bar[i].xp // 10 != 0 else 65
                x_at = 3 if self.my_bar[i].attack // 10 != 0 else 5
                self.screen.blit(xp_text, (236 + 31 * i + 80 * i + x_xp, 407 + 88))
                self.screen.blit(at_text, (236 + 31 * i + 80 * i + x_at, 407 + 88))

                if self.my_bar[i].death_n != 0:
                    if self.my_bar[i].death_n == 60:
                        self.my_bar[i] = 0

                    else:
                        self.screen.blit(self.cross, (236 + 31 * i + 80 * i + x_xp - 15 - 80, 407 + 88 - 105))
                        self.my_bar[i].death_n += 1

    def render_text(self, text, font, gfcolor=pygame.Color('white'), ocolor=(0, 0, 0), opx=1):
        textsurface = font.render(text, True, gfcolor).convert_alpha()
        w = textsurface.get_width() + 2 * opx
        h = font.get_height()

        osurf = pygame.Surface((w, h + 2 * opx)).convert_alpha()
        osurf.fill((0, 0, 0, 0))

        surf = osurf.copy()

        osurf.blit(font.render(text, True, ocolor).convert_alpha(), (0, 0))

        for dx, dy in self._circlepoints(opx):
            surf.blit(osurf, (dx + opx, dy + opx))

        surf.blit(textsurface, (opx, opx))
        return surf

    def my_hand_show(self):
        for i in range(len(self.my_hand)):
            if self.my_hand[i].hov_on:
                self.screen.blit(self.my_hand[i].img, (133 + 29 * i + 100 * i, 490))
                self.my_hand[i].x = 133 + 29 * i + 100 * i
                self.my_hand[i].y = 490

            else:
                self.screen.blit(self.my_hand[i].img, (133 + 31 * i + 100 * i, 526))

    def hover_on(self, mos_x, mos_y):
        for i in range(len(self.my_hand)):

            if self.my_hand[i].img.get_rect(x=133 + 31 * i + 100 * i, y=526).collidepoint((mos_x, mos_y)):
                return i

        return -1

    def show_attacked_min(self):
        for i in range(len(self.my_bar)):

            if self.my_bar[i] != 0:

                if self.my_bar[i].can_attack:
                    pygame.draw.ellipse(self.screen, (50, 237, 50), pygame.Rect(236 + 31 * i + 80 * i, 404, 83, 116), 6)

                else:
                    pygame.draw.ellipse(self.screen, (233, 229, 211), pygame.Rect(236 + 31 * i + 80 * i, 404, 83, 116),
                                        6)

    def hover_on_bar(self, mos_x, mos_y):
        for i in range(5):
            if mos_x in range(223 + 110 * i, 223 + 110 * (i + 1)) and mos_y in range(407, 487):
                return i
        return -1

    def hover_on_op_bar(self, mos_x, mos_y):
        for i in range(5):
            if mos_x in range(230 + 110 * i, 213 + 110 * (i + 1)) and mos_y in range(407 - 275, 487 - 245):
                return i
        return -1

    def draw_arrow(self, screen, colour, start, end):
        self.draw_dashed_line(screen, colour, start, end, 4)
        rotation = math.degrees(math.atan2(start[1] - end[1], end[0] - start[0])) + 90
        pygame.draw.polygon(screen, (255, 0, 0), (
            (end[0] + 20 * math.sin(math.radians(rotation)), end[1] + 20 * math.cos(math.radians(rotation))),
            (
                end[0] + 20 * math.sin(math.radians(rotation - 120)),
                end[1] + 20 * math.cos(math.radians(rotation - 120))),
            (end[0] + 20 * math.sin(math.radians(rotation + 120)),
             end[1] + 20 * math.cos(math.radians(rotation + 120)))))

    def draw_dashed_line(self, surf, color, start_pos, end_pos, width=100, dash_length=8):
        x1, y1 = start_pos
        x2, y2 = end_pos
        dl = dash_length

        if (x1 == x2):
            ycoords = [y for y in range(y1, y2, dl if y1 < y2 else -dl)]
            xcoords = [x1] * len(ycoords)
        elif (y1 == y2):
            xcoords = [x for x in range(x1, x2, dl if x1 < x2 else -dl)]
            ycoords = [y1] * len(xcoords)
        else:
            a = abs(x2 - x1)
            b = abs(y2 - y1)
            c = round(math.sqrt(a ** 2 + b ** 2))
            dx = dl * a / c
            dy = dl * b / c

            xcoords = [x for x in numpy.arange(x1, x2, dx if x1 < x2 else -dx)]
            ycoords = [y for y in numpy.arange(y1, y2, dy if y1 < y2 else -dy)]

        next_coords = list(zip(xcoords[1::2], ycoords[1::2]))
        last_coords = list(zip(xcoords[0::2], ycoords[0::2]))
        for (x1, y1), (x2, y2) in zip(next_coords, last_coords):
            start = (round(x1), round(y1))
            end = (round(x2), round(y2))
            pygame.draw.line(surf, color, start, end, width)


class Creature:
    def __init__(self, name, attack, xp, manacost):
        self.manacost = manacost
        self.attack = attack
        self.xp = xp
        self.name = name
        self.img = pygame.transform.scale(load_image(self.name + '.png'), (100, 160))
        self.hov_on = False
        self.x = 0
        self.y = 0


class Creature_on_board(Creature):
    def __init__(self, name, attack, xp, manacost):
        super().__init__(name, attack, xp, manacost)
        self.img = pygame.transform.scale(load_image(self.name + '_on_board.png'), (80, 110))
        self.at_n = 0
        self.death_n = 0
        self.can_attack = False

    def atack(self, num_of_enem_creature, board, event):
        self.xp -= board.opponent_bar[num_of_enem_creature].attack
        board.opponent_bar[num_of_enem_creature].xp -= self.attack
        self.can_attack = False

        if self.xp <= 0:
            self.death_n += 1
        if board.opponent_bar[num_of_enem_creature].xp <= 0:
            board.opponent_bar[num_of_enem_creature].death_n += 1


# Класс манабар, для будущих наработок
class Manabar:

    def __init__(self, num):
        self.num = min(10, num)


pygame.init()

clock = pygame.time.Clock()
board = Board(1000, 700, 'background.png')
KwantStone = True

while KwantStone:
    if board.music_flag:
        for i in [board.loser_sound,
                  board.winner_sound,
                  board.kick,

                  board.your_turn_sound]:
            i.set_volume(1)
    else:
        for i in [board.loser_sound,
                  board.winner_sound,
                  board.kick,

                  board.your_turn_sound]:
            i.set_volume(0)
    if len(board.my_hand) == 0 and board.my_bar.count(0) == 5 and board.game_start and board.take_card is False:
        board.loset_flag = True
        board.loser_sound_flag = True
        if board.loser_sound_flag and board.music_flag:
            board.loser_sound.play()
        board.loser_sound_flag = False
    if board.opponent_bar.count(0) == 5 and board.game_start:
        board.winner = True
        if board.winner_sound and board.music_flag:
            board.winner_sound.play()
        board.winner_sound_flag = False
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            KwantStone = False

        # Условие для рисовки стрелки
        if event.type == pygame.MOUSEBUTTONDOWN and board.hover_on_bar(event.pos[0], event.pos[1]) != -1 and \
                board.my_bar[board.hover_on_bar(event.pos[0], event.pos[1])] != 0 and board.my_bar[
            board.hover_on_bar(event.pos[0], event.pos[1])].can_attack:

            if board.my_bar[board.hover_on_bar(event.pos[0], event.pos[1])].death_n == 0:
                board.num = board.hover_on_bar(event.pos[0], event.pos[1])
                board.choose_opp = True
                board.arrow_from = 223 + 110 * board.num + 55, 407
                board.draw_arrow(board.screen, (100, 100, 100), (223 + 110 * board.num + 55, 407), event.pos)
                board.at_min = board.my_bar[board.hover_on_bar(event.pos[0], event.pos[1])]

        # Если выбирал существо противника для атаки, но не быбрал
        if event.type == pygame.MOUSEBUTTONUP and board.choose_opp and board.hover_on_op_bar(event.pos[0],
                                                                                             event.pos[1]) == -1:
            board.choose_opp = False

        elif event.type == pygame.MOUSEBUTTONUP and board.choose_opp and board.hover_on_op_bar(event.pos[0],
                                                                                               event.pos[
                                                                                                   1]) != -1 and board.at_min != 0 and board.at_min.can_attack:

            if board.opponent_bar[board.hover_on_op_bar(event.pos[0], event.pos[1])]:

                if board.opponent_bar[board.hover_on_op_bar(event.pos[0], event.pos[1])].death_n == 0:
                    board.choose_opp = False
                    board.attacked_minion = board.opponent_bar[board.hover_on_op_bar(event.pos[0], event.pos[1])]
                    board.at_min.atack(board.hover_on_op_bar(event.pos[0], event.pos[1]), board, event)

                    board.kick.play(maxtime=500)

                else:
                    board.choose_opp = False

            else:
                board.choose_opp = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if board.restart.get_rect(x=906, y=440).collidepoint(event.pos):
                board.hand_update()
                board.game_start = True
                board.loset_flag = False

            elif board.turn_button.get_rect(x=808, y=319).collidepoint(event.pos) and board.game_start:
                board.new_turn()
                board.your_turn_sound.play()

            elif board.exit_button.get_rect(x=907, y=551).collidepoint(event.pos):
                KwantStone = False

            elif board.sound_button.get_rect(x=907, y=511).collidepoint(event.pos):

                if board.music_flag is False:
                    pygame.mixer_music.play(100)

                    board.music_flag = True
                else:
                    pygame.mixer_music.pause()
                    board.music_flag = False

        board.turn_button = load_image('turn_button_green.png')

        for i in board.my_bar:
            if i != 0:

                if i.can_attack:
                    board.turn_button = load_image('turn_button_yellow.png')
                    break

        if event.type == pygame.MOUSEMOTION and not board.take_card:
            num = board.hover_on(event.pos[0], event.pos[1])

            if num != -1:
                board.make_cards_little_again()
                board.my_hand[num].img = pygame.transform.scale(load_image(board.my_hand[num].name + '.png'),
                                                                (135, 210))
                board.my_hand[num].hov_on = True

            else:
                board.make_cards_little_again()

        if event.type == pygame.MOUSEBUTTONDOWN and board.hover_on(event.pos[0], event.pos[1]) != -1:
            num = board.hover_on(event.pos[0], event.pos[1])
            board.i_took_card = board.my_hand.pop(num)
            board.take_card = True
            board.i_took_card.img = pygame.transform.scale(board.i_took_card.img, (100, 160))
            board.i_took_card.x = event.pos[0] - (133 + 31 * num + 100 * num)
            board.i_took_card.y = event.pos[1] - 526

        if event.type == pygame.MOUSEBUTTONUP:
            num = board.hover_on_bar(event.pos[0], event.pos[1])

            if board.i_took_card != -1 and num != -1 and board.my_bar[num] == 0:

                if board.my_bar[num] == 0:
                    name, at, xp, manacost = board.i_took_card.name, board.i_took_card.attack, board.i_took_card.xp, board.i_took_card.manacost
                    board.my_bar[num] = Creature_on_board(name, at, xp, manacost)
                    board.i_took_card = -1
                    board.take_card = False


            elif board.i_took_card != -1 and (
                    board.hover_on_bar(event.pos[0], event.pos[1]) == -1 or board.my_bar[num] != -1):
                board.my_hand.append(
                    Creature(board.i_took_card.name, board.i_took_card.attack, board.i_took_card.xp,
                             board.i_took_card.manacost))
                board.take_card = False
                board.i_took_card = -1

        if event.type == pygame.MOUSEMOTION and board.take_card:

            if event.pos[1] < 510 and 0 in board.my_bar:
                board.i_took_card.img = load_image(board.i_took_card.name + '_on_board.png')

        if event.type == pygame.MOUSEMOTION:
            board.posi = event.pos

    board.allDraw(event)
    board.show_attacked_min()
    board.my_bar_show()
    board.my_hand_show()

    if board.choose_opp and event.type != pygame.KEYDOWN:
        board.draw_arrow(board.screen, (100, 100, 100), (board.arrow_from[0], board.arrow_from[1]), event.pos)

    if board.i_took_card != -1:
        board.screen.blit(board.i_took_card.img,
                          (board.posi[0] - board.i_took_card.x, board.posi[1] - board.i_took_card.y))

    if event.type == pygame.MOUSEBUTTONDOWN and board.take_card is False:
        board.screen.blit(board.handdown, (board.posi[0] + 2, board.posi[1] + 1))

    elif pygame.mouse.get_focused() and board.choose_opp is False and board.take_card is False:
        board.screen.blit(board.cursor, board.posi)

    elif pygame.mouse.get_focused() and board.take_card is True:
        board.screen.blit(board.handgrab, board.posi)

    board.clock.tick(25)
    pygame.display.flip()
