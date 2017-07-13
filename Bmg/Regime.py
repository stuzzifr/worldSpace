from Impots import *
import math
import time

tableauAmortissment = '{:>3} RestantDu: {:9< .0f}\t\tInteret: {:>2,.1f}\t\tCapital: {:>3,.0f}\n'
info = '\nyear {:>2.1f} mensualite:{:>3,.0f} interets:{:>,.0f} total:{:>,.2f} ratio:{:.1f}% renta:{:.1f}%\n'


class Regime():

    def __init__(self, pret, regime, ammortissable=True):

        regime == ['BICMicro', 'BICReel', 'foncierMicro', 'foncierReel']

        # -- init values, annu stand for cumulative
        annuCapital = annuRevenu = annuInteret = annuNetCharge = 0
        year = int(time.strftime('%Y')) + 1
        restantDu = pret.cout
        reimbursed = False
        self.out = str()
        sumInterets = 0
        month = 1

        # -- deduc for reel
        fictive = ((pret.cout - pret.travaux - pret.notaire) * .85) / 20.0
        chargeDeduc = pret.travaux + pret.notaire + fictive

        # -- start parsing
        while True:

            interet = restantDu * (pret.taux)
            capital = pret.mens - interet
            annuCapital += capital
            restantDu -= capital

            # -- feeding graph per MONTH
            # pret.fluxM['Loyer M'].extend([month, pret.loyer])
            # pret.fluxM['Mensualites M'].extend([month, pret.mens])
            # pret.fluxM['Interet M'].extend([month, interet])
            # pret.fluxM['Capital M'].extend([month, capital])

            # -- reimbursed then stop loop
            if pret.annees == month / 12:
                reimbursed = True

            # -- printing last infos
            if restantDu < 0:
                isvalid = 'valid' if pret.ratio < 70 else 'invalid'
                total = pret.cout + sumInterets + pret.ass
                self.out += isvalid
                self.out += info.format(month/12.0, pret.mens, sumInterets, total, pret.ratio, pret.rentabilite)
                self.out += str(pret)
                break

            # -- print every year infos
            self.out += tableauAmortissment.format(month, restantDu, interet, capital)

            # -- interet for a year
            annuInteret += interet

            # -- revenu foncier for a year
            annuRevenu += (pret.loyer * pret.occupation) / 12.0

            # -- loyer - (charges) for a year
            annuNetCharge += (annuRevenu - (pret.charges*12.0) - (pret.ass/pret.echeances*12.0) - pret.fonciere/12.0 )
            # rajouter comptable? + CFE?

            # -- netCharge = loyer - (charges + taxe fonciere)
            # -- tresoBrut = netCharge - traite
            # -- tresoNet = tresoBrut - impot\n'''

            # -- At the end of the year
            if not month % 12:
                if not reimbursed:

                    if regime == 'BICreel':
                        annuTresoBrut = annuNetCharge - (pret.mens * 12)  # -- avant impots
                        imposable = annuNetCharge - annuInteret - chargeDeduc

                        if imposable < 0:
                            chargeDeduc = abs(imposable)
                            imposable = 0

                        else:
                            chargeDeduc = 0

                        chargeDeduc += (((pret.cout - pret.travaux - pret.notaire) * .85 ) / 20.0 )

                    # -- abattement 50%
                    if regime == 'BICMicro':

                        comptable = 300 # a verifier
                        CFE = 500 # a verifier

                        annuNetCharge = annuRevenu - (pret.ass/pret.echeances*12.0) - CFE - comptable - (pret.charges*12.0) -  pret.fonciere
                        annuTresoBrut = annuNetCharge - (pret.mens*12)

                        chargeDeduc = 0
                        imposable = annuRevenu * .5

                    if regime == 'foncierMicro':
                        # -- abattement 30%
                        imposable = annuRevenu * .5

                    if regime == 'foncierReel':
                        imposable = annuNetCharge - annuInteret

                else:
                    annuTresoBrut = annuNetCharge + (pret.ass)  # -- avant impots
                    imposable = annuNetCharge
                    restantDu = 0

                revenu = Revenu(revenu=126770, quotePart=2.5)
                foncier = Foncier(revenu, imposable)
                impot = foncier.total

                annuTresoNet = annuTresoBrut - impot  # -- apres impots

                annuRevenu, annuNetCharge, annuTresoBrut, annuTresoNet, restantDu, impot, chargeDeduc = map(int, [annuRevenu, annuNetCharge, annuTresoBrut, annuTresoNet, restantDu, impot, chargeDeduc])
                pret.sheet.setdefault(year, [annuRevenu, annuNetCharge, annuTresoBrut, annuTresoNet, impot, chargeDeduc])

                # -- purge for next year
                annuCapital = annuRevenu = annuInteret = annuNetCharge = 0
                year += 1

                # yearRel = year - (int(time.strftime('%Y')) + 1)
                # pret.fluxY['Revenu Y'].extend([yearRel, annuRevenu])
                # pret.fluxY['TresoBrut Y'].extend([yearRel, annuNetCharge])
                # pret.fluxY['TresoNet Y'].extend([yearRel, annuTresoNet])
                # pret.fluxY['Impot Y'].extend([yearRel, impot])

            sumInterets += interet
            month += 1

    def __str__(self):
        return self.out
