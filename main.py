# naimportování knihoven
import random
import os
import pygame

# inicializace pygame
pygame.init()

# nastavení snímků za vteřinu (fps = frames per second); čím méně snímků, tím bude hra pomalejší
meric_snimku = pygame.time.Clock()
fps = 60

sirka_okna = 864
vyska_okna = 736

screen = pygame.display.set_mode((sirka_okna, vyska_okna))
pygame.display.set_caption('Nesmírně těžká hra')
pygame.display.set_icon(pygame.image.load('./soubory/obrazky/ikona.jpg'))

# nastavení fontu pro počítadlo skóre
font = pygame.font.Font("./soubory/fonty/HydrophiliaIced-Regular.ttf", 60)

# barva písma
barva_pisma = (0, 0, 0)

# proměnné
rychlost_hry = 6
je_ve_vzduchu = False
je_konec_hry = False
mezera_mezi_sloupy = 250
pravidelnost_sloupu = 1500  # milliseconds
posledni_vygenerovany_sloup = pygame.time.get_ticks() - pravidelnost_sloupu
skore = 0
prosel_mezi_sloupy = False


def get_top_hrac_ze_souboru():
    return open(r"./soubory/top_skore/top_skore_hrac.txt", "r").readline()


def novy_top_hrac():
    open(r"./soubory/top_skore/top_skore_hrac.txt", "w").write(str(os.getlogin()))


def get_top_skore_ze_souboru():
    return open(r"./soubory/top_skore/top_skore.txt", "r").readline()


def nove_top_skore(top_skore):
    open(r"./soubory/top_skore/top_skore.txt", "w").write(str(top_skore))


# obrázky
pozadi = pygame.image.load('./soubory/obrazky/obloha.jpg')
tlacitko_reset_img = pygame.image.load('./soubory/obrazky/restart.png')


def vykresli_text(text, font_, text_col, x, y):
    img = font_.render(text, True, text_col)
    screen.blit(img, (x, y))


# procedura která vypíše text skóre
def vykresli_skore(text, font_, text_col, x, y):
    img = font_.render('Skóre: ' + text, True, text_col)
    screen.blit(img, (x, y))


def vykresli_tophrace(hrac, font_, text_col, x, y):
    img = font_.render('Top hráč: ' + hrac, True, text_col)
    screen.blit(img, (x, y))


# funkce která umístí postavu do startovní pozice a vrátí nulu + vymaže sloupy
def restart_hry():
    sloupy_skupina.empty()
    hlavni_postava.rect.x = 100
    hlavni_postava.rect.y = int(vyska_okna / 2)
    # vrátí 0 která bude použita na vynulování skóre
    return 0


# třída Ptak, nastavující jeho vlastnosti
class Ptak(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        self.index = 0
        self.pocitadlo = 0
        # cyklus, který zajišťuje animovaný pohyb ptáka
        for num in range(1, 4):
            img = pygame.image.load(f'./soubory/obrazky/ptak_animace{num}.png')
            self.images.append(img)

        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.pohyb = 0
        self.kliknuto = False

    # stále se opakující metoda
    def update(self):

        if je_ve_vzduchu:
            # gravitace
            self.pohyb += 0.5
            if self.pohyb > 8:
                self.pohyb = 8
            # podmínka která zajišťuje, aby pták nebyl nepadal mimo obraz
            if self.rect.bottom < 768:
                self.rect.y += int(self.pohyb)  # posun ptáka na ose y (směrem dolů)

        if not je_konec_hry:
            # skok
            if pygame.mouse.get_pressed()[0] == 1 and not self.kliknuto:
                self.kliknuto = True
                # pohyb nahoru o 10 bodů
                self.pohyb = -10
            if pygame.mouse.get_pressed()[0] == 0:
                self.kliknuto = False

            # animace
            self.pocitadlo += 1
            prodleva_mezi_animacemi = 5

            # zajišťuje pravidelné střídání obrázků v animaci
            if self.pocitadlo > prodleva_mezi_animacemi:
                self.pocitadlo = 0
                self.index += 1
                # po třetím obrázku se index nastaví na 0, aby animace probíhala od začátku
                if self.index >= len(self.images):
                    self.index = 0
            # načte obrázek z pole s příslušným indexem
            self.image = self.images[self.index]

            # rotace ptáka
            # použití metody rotate z knihovny pygame, která naklání ptáka při pohybu o (self.pohyb * -2)°
            self.image = pygame.transform.rotate(self.images[self.index], self.pohyb * -2)
        else:
            # po nárazu padá zobákem dolů (nakloní se o 90°)
            self.image = pygame.transform.rotate(self.images[self.index], -90)


class Sloup(pygame.sprite.Sprite):
    def __init__(self, x, y, pozice, mezera):
        # nastavení vlastností sloupu
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('soubory/obrazky/panMasarykJakoSloup.png')
        self.rect = self.image.get_rect()

        # pokud je pozice 1, tak se obrázek vykreslí vzhůru nohama
        if pozice == 1:
            self.image = pygame.transform.flip(self.image, False, True)
            # nastaví pozici obrázku
            self.rect.bottomleft = [x, y - int(mezera / 2)]
        if pozice == -1:
            self.rect.topleft = [x, y + int(mezera / 2)]

    def update(self):
        self.rect.x -= rychlost_hry
        if self.rect.right < 0:
            self.kill()


class TlacitkoReset:
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    # pokud se pozice myši a tlačítka shodují a dojde ke kliknutí, tak se nastaví action na True a hra se znovu spustí
    def draw(self):

        action = False

        pos = pygame.mouse.get_pos()

        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1:
                action = True

        screen.blit(self.image, (self.rect.x, self.rect.y))

        return action


ptak_skupina = pygame.sprite.Group()
sloupy_skupina = pygame.sprite.Group()

# přiřazení proměnné hlavni_postava instance třídy Ptak
hlavni_postava = Ptak(100, int(vyska_okna / 2))

# do skupiny ptak_skupina se přidá proměnná, která ukládá instanci ptáka
ptak_skupina.add(hlavni_postava)

# instance třídy TlacitkoReset, která bere parametry x, y, obrázek
tlacitko_reset = TlacitkoReset(sirka_okna / 2 - 50, vyska_okna / 2 - 100, tlacitko_reset_img)

hrajespustena = True
while hrajespustena:

    # načítání smínků každých 60 ms
    meric_snimku.tick(fps)

    # vykreslí pozadí z levého horního rohu z pozice 0, 0
    screen.blit(pozadi, (0, 0))

    # vykreslení ptáka na obrazovce
    ptak_skupina.draw(screen)
    # obnovování skupiny
    ptak_skupina.update()
    # vykreslení sloupů
    sloupy_skupina.draw(screen)

    if len(sloupy_skupina) > 0:
        # v momentě, kdy je ohraničení ptáka přesně pod ohraničením sloupu, dojde ke splnění podmínky --> pták prošel
        if ptak_skupina.sprites()[0].rect.left > sloupy_skupina.sprites()[0].rect.left \
                and ptak_skupina.sprites()[0].rect.right < sloupy_skupina.sprites()[0].rect.right \
                and not prosel_mezi_sloupy:
            prosel_mezi_sloupy = True
            # poté, co je pták již za sloupem, dojde k zvýšení scóre o 1
        if prosel_mezi_sloupy:
            if ptak_skupina.sprites()[0].rect.left > sloupy_skupina.sprites()[0].rect.right:
                skore += 1
                prosel_mezi_sloupy = False

    # vypsání aktuálního skóre
    vykresli_skore(str(skore), font, barva_pisma, int(sirka_okna / 2 - 110), 20)
    vykresli_text('Top skóre: ' + (get_top_skore_ze_souboru()),
                  pygame.font.Font("soubory/fonty/HydrophiliaIced-Regular.ttf", 30), barva_pisma,
                  int(sirka_okna / 2 - 110), 100)

    # vypsání top hráče
    vykresli_tophrace(str(get_top_hrac_ze_souboru()).upper(),
                      pygame.font.Font("soubory/fonty/HydrophiliaIced-Regular.ttf", 20),
                      barva_pisma, int(sirka_okna / 2 - 110), 150)

    # kolize
    # pokud se pták střetne se sloupem a nebo je pták příliš vysoko, tak se hra ukončí
    if pygame.sprite.groupcollide(ptak_skupina, sloupy_skupina, False, False) or hlavni_postava.rect.top < 0:
        je_konec_hry = True

    # pokud pták klesne příliš nízko → pták není ve vzduchu a je konec hry
    if hlavni_postava.rect.bottom >= 768:
        je_konec_hry = True
        je_ve_vzduchu = False

    # pokud nedojde ke splnění výše uvedených podmínek, tak nastane tato podmínka
    if not je_konec_hry and je_ve_vzduchu:

        # nove překážky
        ted = pygame.time.get_ticks()
        if ted - posledni_vygenerovany_sloup > pravidelnost_sloupu:
            # vygenerování náhodné výšky sloupu
            vyska_sloupu = random.randint(-100, 100)
            if 2 < skore < 10:
                mezera_mezi_sloupy = 200
                rychlost_hry = 6.5
            if 10 <= skore < 20:
                mezera_mezi_sloupy = 180
                rychlost_hry = 7
            if 20 <= skore < 25:
                mezera_mezi_sloupy = 150
                rychlost_hry = 8.5
            if skore >= 25:
                mezera_mezi_sloupy = 125
                rychlost_hry = 10
            # vytvoření dvou instancí sloupů
            dolni_sloup = Sloup(sirka_okna, int(vyska_okna / 2) + vyska_sloupu, -1, mezera_mezi_sloupy)
            horni_sloup = Sloup(sirka_okna, int(vyska_okna / 2) + vyska_sloupu, 1, mezera_mezi_sloupy)
            sloupy_skupina.add(dolni_sloup)
            sloupy_skupina.add(horni_sloup)
            posledni_vygenerovany_sloup = ted

        sloupy_skupina.update()

    # když nastane konec hry, tak se vykreslí tlačítko a skóre se nastaví na 0
    if je_konec_hry:
        if tlacitko_reset.draw():
            je_konec_hry = False
            skore = restart_hry()

    # cyklus, který proběhne pokaždé co pygame zaznamená událost
    for event in pygame.event.get():
        # dojde k porovnání událostí
        match event.type:
            # pokud uživate zavře okno
            case pygame.QUIT:
                hrajespustena = False
            # pokud uživatel zmáčkne tlačítko na myši
            case pygame.MOUSEBUTTONDOWN:
                if not je_ve_vzduchu and not je_konec_hry:
                    je_ve_vzduchu = True

    if je_konec_hry and int(get_top_skore_ze_souboru()) < skore:
        nove_top_skore(skore)
        novy_top_hrac()

    # po doběhnutí celého cyklu while, se display aktualizuje
    pygame.display.update()

# konec hry
pygame.quit()
