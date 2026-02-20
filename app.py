"""
Note de Frais – Application Streamlit v3
Nouveautés :
  - Montants en format français (1 234,56)
  - Logo + adresse selon la société choisie
  - Signe de devise dynamique (€ / $)
"""

import io
import base64
import json
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from datetime import date
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle,
    Paragraph, Spacer, KeepInFrame,
)
from reportlab.platypus import Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import mm
from pypdf import PdfWriter, PdfReader
from PIL import Image as PILImage

# ─── Logos embarqués en base64 ────────────────────────────────────────────────
_IFEA_LOGO_B64  = "/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAUDBAQEAwUEBAQFBQUGBwwIBwcHBw8LCwkMEQ8SEhEPERETFhwXExQaFRERGCEYGh0dHx8fExciJCIeJBweHx7/2wBDAQUFBQcGBw4ICA4eFBEUHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh7/wAARCADIAbsDASIAAhEBAxEB/8QAHQABAAICAwEBAAAAAAAAAAAAAAEIBwkCBQYEA//EAFUQAAEDAwIDAggGCg4JBQAAAAEAAgMEBREGBwghgRIxEyJBUWFxkaEJFDIzkrEVFyM3VVZ0k8LRFhg2OEJSU2Jyc3aUsrQkJTVDVIKiweEnKDRE0v/EABcBAQEBAQAAAAAAAAAAAAAAAAACAQP/xAAeEQEBAQEBAQEBAQEBAAAAAAAAAQIRMRIhA0FRE//aAAwDAQACEQMRAD8AuWuE3zZXNcJvmyg5Du7k6IO7vTqgdE6Jn0rz2stZ6d0lSGqvt0p6RmMhrnjtO9QzkoPQ8/MnRYssO/22d7uAoKO/COUuwDOwRt9pKyfS1EVTAyeGVkkbxlrmHII9aco/TonROqdUDonROqdUDonROqdUDonROqdUDonROqdUDonROqZ9KB0Tovjr7rbKD/51xpab+tlaz6yvnpdR6fqpBHTXy3TPPc2OpY4+4oO06J0QOBAIcCD3Jn0oHROidU6oHROidU6oHROidU6oHROidU6oHROidUz6UDonRM+lM+lA6J0TPpTPpQOidE6p1QOidE6p1QOidE6p1QOidE6p1QOidE6p1QOidE6pkedA6J0XW1l/sdG8sq7zb6dw7xJUMafeV+lDerRXu7NFdaKpPmima76ig+7onRMjzp1QOilOqIC4TfNlc1wm+bKDkByTCgdylB8t4qRRWuqrD/uYXyewErVrvduBdtfa3r7jXVL3UolIp4c+Kxvmwto2oKZ1bZK2kb8qaB7B6y0handxdOV+lNYXGy3GB8UtPMW+MPlelXhOq6BjnMeHscWuByCFeDgM3HuV9t1fpO81jp30mHUjn5Li05JGfMAAqOq4fwe+j61lVc9WVUEkUGBHTOcMCTvDsepXrxkXOATCIuKzCYREDCYREDCYREDCYREHCaRkMbpJHBrGjJcTgAKpPEZxRC1VdVpzQhZLUxnsS1rhloPc4Acjy588rIPGXuLJozbl9voZvB3C5fc2YOD4M5Dj7wtdEj3ySukkcXPcSXOPeSrxnv7U2vR6h13q6/VT6i6X+vnLzktMzuyPUM8l1tFqC+UUolpLtWQPHMOjlIK61F0Sz/sxxNau0ncqek1FUPu1oPiyeEOZW+Y9ok8h5lfHQmq7RrDTtPerNUtnp5255Hm045grUerIcDu48+n9ct0rXVhZbK8HsB58Vjxk8vSThTrKpWwDCYQFFyUYTCIgYTCIgYTCIgYWFOMfUt60ntSLpYqx1JVfHGM7bSc4Idy5epZrVfOPU/8AomPy+P8AwuW59ZVP/t8bn/jHP9J360+3xuf+Mc/0nfrWNYoZpXBsUT5CfI1pK9bpfbDXmpnNFm01XVQPlDQMe0hdeRH6737e+5/4yT/Sd+tdlpXfDcqp1JQU8+oZ3RyTta4dp3MZ9a9nonhE1xd2ia81lNaGeWKZru37shZp0Bwk6RsVdBcbrcKquqYXBzWgjweR6CMrLct5VibDI+ex0E0jsvkpo3OPnJaCV9mF+VLCympYqeMYZEwMaPMAMBfquSzCYREDCYREDCYREDCYREHWakvdt0/Zqm63WpbT0tMwvke49wCozvnxR6hv1fLbNHPNstzO0x0vfJIfIWuGCF6Lj33HqJLnBoa21LmwMaX1gY7vdkjsnphVFXTOf9Ta7e5am1DcpjLXXmuqHuOSZJnOK/ey6x1RZp2zW2+19M9pyOxO4D3FdEi6IW84euKatbWwWHXzmyxSPDI61o7PYH87vJVzaCqgrqSKrpZGyQytDmOacggrTtzV8OBPcqW/6aqdJ3WrdJW0JHxbtnLnR4JPs5LnrP8AsXKtDhFAKlc1C4zfNlclwm+bKDmO5MrqtTX+0abtEl1vNdDSUsY5vkcBk+YZ7yqubjcY1uoK59LpCz/ZCNhLTNUExcx5hg5C2S1nVtzzWMN5dktIbm0zjc6cUlw7PZZXQtzI328lU6s4vtfy1PbgpaWCPPyAQ734XoNOcZt9injZeNO000WfHkbMcgeoBV81nY9/prg10hbbxDW19/uNygicC6mmjYGSDzHHNWQ07Y7Xp+1xWy0UcVJSRDDI4xyC8XtLvBo/celDrLcA2qA8emmAZJ6cAnJHpWRhhTe/6rgiYTCwETCYQETCYQETCYQETCYQUS+EPq5pNdWSmcT4OOmkwP8Amaqtq5nwh2k6maGz6rhjJgp2ugmI8jnuGPqVM12x4569ERFTBeg22mkg17ZJIyQ4V0IyPS8Lz6yLw56Uq9X7r2i30reUUwne49wDD2v+yy+NjaWw5YDjGVKgBThcHQRMJhARMJhARMJhAXmNxtEWXXlnhtF+h8PRxztmdGe55GeR9HNenwvhvV1t1nonVtzrYKOnZ8qSV4a0dSg8jpjaDbnTc7Z7PpWgppm9zwHE+8le1p6WngGIoIo/6LAFXfcjiy0Tp+SajsUct2rIjjm0tiPqeM5WJa3jO1RK8/F9NUcLfJ/pBP6Kr5tZ2L04RUSpeM3VkZBm07RzDyjw5H6KyVt7xgaWur46fVFBLa5nuDWmFpkb6yTjCfFh1aNF0+l9SWTUtC2tstyp62EgHMUgd2fQcdxXcYCloiYTCAiYTCAiYTCAuMp7MbnDvAJXLCggEEHyoNXHE5VzVe+Gp5JiSRWuAz5BgLGyzfxoaVqbBvJcK90ZEFzeaiN2OWM4x7lhBd5450REWsFn7gSq5afe+KNhPZkopg4fRWAVaP4PvSlbVa6rNUmH/Q6OB1OXH+M8AjHsKnXjZ6vcO5FAHJSuLoL8qxzWUz3uOA0ZK/Vea3QrpLboO6VsRw+NjMH1yNH/AHQUI4uN1a/Wmt6izUlU9lnt7jHHG12GyHvyR5SDkLBRX1XmR0t4rJHklzp3kn/mK52C3y3e+0Frh5Pq6iOAHzFzg3PvXefkc/Xwp3rY3oLhp28s+lYqG62llwrpI/u88zQ5weRz7JxyHmVRuKna6j2y1xHR2p8j6Cri8NF2zkt5kY9yyalbYxto3Ul00nqCmvVpqZIKiB4cOy4gOGe4+cLaFspren19t7btQQjsukb4OUfz24Dj7crVIr0fB43Weq0VdbVI4mKjlDmDzdpxJWbn50zVqcplApwuS0ZTKnCYQRlMqcJhBGUypwmEEZTKnCYQea3J0pb9a6QrdP3FjXRVDCGkjPZdggO6ZWs3eDbLUO3WpJ7ddKOQU/aJgnaMsezPLn3ZxhbViAV0esNI6e1bbXW+/wBsgroSCGiVoPYJ8o8xVTXGWdailKvTrDg50xWSvl0/daijc457M7u00eoALpbHwXwR1LXXfUbJoc82wBzXY6hdPuJ+VO7TbLhdq+KhttLNU1Erg1rI2Fx5+pbBeEfZn7X1gN6u8TTeq1oLgefg294A8x5r221myuh9vWtfaLaJasf/AG6jDpR5wDjuWSgAFGtdbJwymVOEwoUjKZU4TCCMplThMIIymVOF8tyq4aChnrKh4ZFDGZHknyAZQeY3W3Asu32l57zd52jstPgogfGkd5gtdu9O82qdx7tK6qrJaa2AkRUsbi1vZ/nY5FfXxOboVm4uvaoxVJdZqSQsoo2nxS3nh+PPg96xMuuc8/UWihZl2I2C1LuU9lc//V1oDudRK0+OB3huOatvovhc2ysLQ+qopbpMWgO+NEPbn0DC26kZxrjRbKNW8M+119gDGWk21w7nUeIz9Sq3vxwz3/Q0M14sUhulpZlxa0EyRN/nE9/RJqVvGMdrty9UbfXiKtstfI2EOBkp3OJjePL4ucZ9K2H7Ebt2Xc3TjKqmkbDcIxiopy7xmnzj0ZWrxzS1xa4EEHBBXstmtdXLb/XFHe7fM5jO21tRHnxXszjmPLjJKzWekra6CmV0+jr/AEWptOUN7t8gfTVkQkYQc8iu5wuS0ZTKnCYQRlMqcJhBGUypwmEGH+JvaWHc3SDmUzWsu1IC+lfnHaOPkk+bmtcWqNP3bTd3ntd3o5aaeFxaQ9pAOPKD5Vt8LQRgrwm5+0+jNwKR0V9tcZqCMNqo2gSt9TsKs64yzrVUiurqLgxt8tQXWLUBp4vI2p7Tz7gvq0rwaWKnmD9Q3uWqaDns0zizPtCv6ifmqjbdaIv2udQQWiy0ckr5HAOk7J7DB5ye5bMNkdv6DbnQ9NY6RoMvZDqh/le//wAZK7Hb/QGltD29lJp61w0uG9l8oaA+T0uPlXqQAFGtdbIAqUwilQvLbr0NXctv7pRUMD56iVsfYjYMl2JGE+4FepXCb5opBrCr9iN3ZK6d7NB3ktdK4giHvGfWu4282R3Wt+urHW1miLtDTwV8EksjouTWiRpJPPzLZMAMJgK/upmUqkPwi/7q7H+SfpOV3sqkPwi37q7H+SfpOWY9brxU1XW+Dk/2PqT+lF9blSlXV+Dl/wBj6k/pRfW5dN+Ii3YBU81APJMri6J5pzUZTKCeac1GUygnmnNRlMoJ5pzUZTKCeac1GUygnmnNRlMoJ5pzUZTKCeac1GUygnmnNRlMoJ5pzUZTKCeawjxl6vfpbaOqjgkMdVXnwURB8mR2vcVm3Kp98I3XSfY7TlCHEN8NI4jz+K1bn1lUvHcvXbR2ay3zXVvotQ3CKgtfhA6plkOAGZ5ryIXJrnNOWuLT6Dhd0NoOndyto7Faaa2W/WNmip6eMMY1smO4Yz3LshvJtf8AjtaPzv8A4Wq7wsv8q/6RTw0v8q/6RXP4b9NqP25Nr/x2tH53/wAL8K3dnamsp309RrKzSRPb2XMdJkEexatfDS/yr/pFPDS/yr/pFPg+mTeJOy6UtW4E9Ro660tfbKv7oPAHIY48yPaVi9S573/Le53rKhWle34P/WTbno2s0tUSufVULvCRAnuiwAPeVaTmqGfB4VRh3KvEPkkoAMf84V8srlqfrpE805qMplS1PNOajKZQTzTmoymUE805qMplBPNOajKZQTzTmoymUE80TKIC4TfNlc1wm+bKDkByTCA8kygYVIPhFv3W2T8k/Scrv5VIPhFv3W2T8k/Scqx6zXipyur8HL/sfUn9KL63KlSur8HKR9h9SeftRfW5dN+Ii3TiGtyTgL5/j1F/xlP+cH618mq5Hx6auMjHFrm00haQeYPZK1X1+vtaNrZmt1PdAA84/wBId51yznqreNrgrqIkAVdOSe4CQL9xzGRzC1YaE13rGfWVohm1Jc5I31cYc11Q4gjK2iWNznWWhc4kudTxkk+U9kLbnjZevswmEymVLTCYTKZQMJhMplAwmEyvwrquGjp5KmplZDDG0uc95wAAg/dQThVe3i4s7LYKua1aTpTcaqMlrqkkeDafNg96wVc+K7dSqnc6Oot0LM8g2nP/AOlUxazrYsOanC12Wjix3Ro6hrqia3TxZ8Zppzk/9SsFs1xUac1VURWvUcRtNc8hrZHEFkhPmAHLqlzYdWRwmFwhlZNG2SJ7XscMtc05BHrXPKlphMJlMoGEwmUygYVQPhGrfIbZpyvDSW+GkaT5sNarf5WFuMTSL9VbR1hp4y+rofusWB3DI7XuC3PrK1sL1u2G32oNxb1JaNOsp5KpkZlLZZmx5aMd2fWvI+te02X1rNoDX9v1DH23QxSAVDGnBfHnJHuXaoZG/anbt/g63/31in9qdu3+Drf/AH1iv1ozU1s1VYaW8WqpZNBPGHYa7JaSOYPqXdj1lcvqq+Y11ftTt2/wdb/76xP2p27f4Ot/99YtivUqHuaxpc54a0d5J5BPqnI11/tTt2/wdb/76xP2p27f4Ot/99YrwVm6mhKOrkpqjUVIyWM9lw7WcFfl9t3b38ZaX2lPrR8xg/hF2P1pt1ravu2p6amhglpRHEYqhshLu0D3D0K1eF0GltXWDUpebJcI6xsfyiwHA6rv8rLbfWwwmEymVjTCYTKZQMJhMplAwmEymUDCYTKZQMJhMplAwpUZUoC4TfNlc1wm+bKDkMYU8lAzhTzQOSpr8IvaH/6jvYB7Gfi/Xxirk81jjiE29i3G28rbOAwVzGl9G93c2Tu+rK3N5WVq2WbeFTeWDay91kNzpXz2y4BvhSwjtsLc4Izyxk81ifVenrrpi9T2m80c1JUwvLSyRuCceVdSu1nULx7tcVmlptIVVDpiCaeuqYzG1ziOyzPfnplUfkeXyOee9xyVxUepZMyHevU7TUjq7cvT1I0EmSvib/1BbYbbF4C308B744ms9gAVKuCbZusmvceutQ0JZRwtPxOOUEFz+RDx6iFdtmcLnu/qsxy5JyTmnNSo5JyTmnNA5JyTmnNBBICqNx4bpVVsEWg7TO+GWVgkrC04PZIBaPrVuT3LWZxeXeS8733Wok5eCYyAD0MyFWJ2srEXM9/egBPcCfUoPcrwcJuxOj7htzQ6r1HbY7nUXOPwsYkyBG3JGBg+cLrbxEnVICCO8EKWOdG9r2Etc05BHkKuhxacP9hotKs1Joi0yQVsUrYn0dO0uEocebjk55Y96qp9r7W34sXP8wVkvSxc/gZ3QqNUadm0ldqh8tdbIw6J7jnMWQ0D25VnOSoRwWWDVent2GvrrJXUlNURiOSSSMtaACSr7DOFz16ueJ5JyTmnNS05JyTmnNA5L5rhSxVtHNSzMD4poyx7T5QRgr6eac0Gs7ik2sqtu9d1MtNTdmy1shfSOY3xWA58T14Cw8ts+52hbJrzTFRZbzTte2RpEcmMujd5wteW92xuqtublNK6lkrLQSXR1UYyGt8zuWAV1zpFj4dl95tVbZVv+rag1Fvd85RyE9g+nHnVsNI8XehrhRx/ZekqbfU4HhO25vZz6OfcqCKFtzKyVsVuPFZtnTQl8VRLUuH8GNwyfasF7y8WN31FR1Fp0jSSWuklHZM7z92x6CDhVeRJmRvX61E8088k80jnySOLnuJ5kk5JX72miq7pcYKCjY+WeZ4YxreZySvs0npi+apukdusVunrah7gOzE3PZB8p9CvNwxcO1NohjNRapbHU3t3zcWMsgHkIPn5nOUuuHHvOGHbk7d7c01DVNH2QqsTVXLufjBHuWWOS4tGAMcly5rjb1ZyTknNOaByTknNOaByTknNOaByTknNRz86CeSck5pzQOSclHVOqCeSJzRAXCb5srmuE3zZQcgeSZQDkpwghDjHcpwmEGP90NptIbhUhivluYZv4M8Y7LwfSRzKrzqzgwjc902n9RvwTyhkiAA6kq4uEx6Vs1Yzijlr4MtQyVIbcL7FTw55uYGvPsysv7b8K2h9LVsNdcnyXiphIcx0g7Lc+luSCrCY9KYW3VOPwoqWno6dlNTQxwwxjDWMaGgD1Bfv0U4TClqMplThMIIymVOEwgjK+eurqShjElZUw07CcB0rw0E9V9OFW34QCsrKHay2y0VVNTyG4tBdG8tOOw7zJJ2jPp1FYcZ+zFB/eG/rWsbiNmiqN3b1LBIySN0pw5pyD4xXkf2R3/8ADNf+fd+tdbUTTVErpZ5XySO73OOSV1zniLevzWzHhbvdnp9g9JQz3OjikZRYcx8zQQe27vGVrPXYU19vNNAyCnulZFEwYaxkpAA9S3Wesl421S33TsrOxLdLbI3zOmYR9a/H7JaT/wCLs/041qg/ZJf/AMM1359360/ZJf8A8M1359361H/mr6bZqGu09LUNZRVFtfMfkiJzO0fYu1BWubg9vV3rN8LNBVXOrmidJza+UkHxXLYw0clNnGy9TlMqcJhY1GUypwmEEZTKnCYQQvkudvo7lTOpq2lhqIXDBZKwOHsK+zCYQYA3B4WdA6mqpayibJaqmTmXR5Lc+huQFhy/8GV+gncLNfY6uPPIyhsZ+tXiwowqmqziiFDwb6wkma2sudNDH5XNe1xHTKyRpPg30vQujkvt5qLnj5TAzwfvBVp8JhLqnHl9D6C0to6iZS2K009OGDHbLAX/AEu9eo5eZThMKWo5eZMqcJhBGUypwmEEZTKnCYQRlMqcL566qgoqaSpqZWRQxt7TnvdgAIP3JHlX41NXTUsRlqZo4Yx3ue4NHvVWd8+K2isks9n0TGyrrY3Frqp47UbT6j3+1VS1fuvr3U9fNV3DUVcwTHLoYZnMiHqbnAVTNqbWzap15oymeWT6os8bh3h1ZGD9a/e36v0vcXhlDqC11Lj3CKqY4n2FakKiqqah5fPPJK495e7JX0W673S2yCSguFTSvHc6KQtI9ir4PpuBD2uGQQV+FXX0VI4NqquCAu5gSPDc+1a5NpuJDXWi6iOGtrZLvb3SB0rKkl8hHma5x5LvuKzd+LWz9LXXS9zq6MfE5RUwxylpa/tjGcYz5VPxekq/MV3tcsjY47jSPe9wa1olBJJ7gOa+5attk9T6iqN5dEQT3uvkik1DQMex07iHNNRGCCM92FtJTWeNl6LhN82VzXCb5sqWuQ7u5OiA8lOUEdE6KchMoI6J0U5TKCOidFOUygjonRTlMoI6J0U5TKCOidFOUygjoq9cddgvOotsrfR2W3zVs7Lg17mR4yB2Xc1YbK4SRxyfLaHD0jKS8GqT7VW4X4q1/sb+teVudBWWytkoq+nfT1EZw+N3eFuCNPB/Ix/RC1dcSbWt3hvYaAB4U939IrrnXUWcY5XqbTt3rW7W6G427TtZU0s7e1FKwDDh5xzXlh3hbPeFWKF3D9o9zomOJoeZLR/Hct1rjJOte32qtw/xVr/Y39afaq3D/FWv9jf1rax8Xp/5GP6IT4vT/wAjH9EKPtXyoDwnaA1jZN57PX3XT9XS0scmXyPAwPFd6VsBachcWwwtOWxMB84aFzGApt62Th0TopymVjUdE6KcplBHROinKZQR0TopymUEdE6JkKcoI6J0U5TKCOidFOUygjonRTlMoI6J0U5TKCOidFOUyg4SODY3OcQ0AZJ8wVHOMXfSsuN2qNEaZrXMoYCWVcsTvnHdxb0IVjeKPXo0LtdX1UUvZrKpvxeFoPjeP4pI9WVrLqZ5amofPPI6SWQ9p7nd5PnV4n+ptflzJyeZX608E9Q8Mp4ZJXHyMbkru9v9J3XWuqKOwWiIvqKl4aDjk0HylbENj9h9Jbf2qGSWijrruWjwtTM3LgfKB5Pcrt4mTqg9l2k3HvNOKi2aSuFREe5wDR9ZXzai2z15p6Lwt50zXUjPO5oP1Era7FTwRN7McTGDzNaAuFTRUlSwsqKeORp5EOYCo+1fLTw9j2PLHtcxw7w4YIUK/nEhw5WTVFuqr5pOhjor03Mj44hynPp7+fqVC7lRVFurpqKqjdHNC8se094IOF0l6mzj1Oxn37NCf2kt/wDmY1tgWp/Yz79mhP7SW/8AzMa2wKP6KyLhN82VzXCb5srmpyA5JhAeS/Opnjp6eSeZ7WRxtLnOccAADJKDk9waC5xAAGSV4rVe62gtMhwumoaMSN74o5WueOmVVLig4kbhcbjU6V0XUmno4XGOoq2HxpD3ENI5ju7wqs1tXVVsxmq6maokccl8jy4nqVcx31N02X23iK2sr6ptPHfHROJx2pWBrfblZHsOobJfoPD2e50tczHMwyB2PYtQa9VoDcDVOirvDcLJdJ4vBnnE55Mbh5QW5wtuITTbMmFiThy3it26Gnx23Ngu9M0fGYe7Pk7Q9ZzyWW8rnfxRhMJlMoGEwmUygYTCZTKBhMJlMoC1bcSv3475/XH/ABFbSVq34lfvx3z+uP8AiKv+fqdeMbhbQOFP977o/wDIf03LV+FtA4U/3vuj/wAh/Tct/p4zPrKGEwmUyuazCYTKZQMJhMplAwmEymUDCYTKZQMJhMldRq/UVt0tYKq+XecQUdLGXyO8uB5h5Sg7CrqqekhdNUzMiiaMue84A6rH2pt7tttPymKs1FTyvHItp3NkI96pHv3v/qXX10npLZVTW6yteRFFE4te8A95cMHn34WFZJHyvL5Hue497nHJK6TH/UXTZ9p7fvbG91AgptQRwOPd8YLYx7ysi2240Nypm1NBVQ1MLu58Tw5p6haemuLXBzSQR3ELJ2zm9GrdvLrHJBXzVdvLwZqWZxeC3yhufkpcf8PptCwmF5LavXdo3A0nS360Sh0cjcSMPymOHeCPXletyuazCYTKZQMJhMplAwmEymUFLvhFL259fY7Ix/KMOfI3PnDSFUBWW+EDLzunAD8j4uzH0Qq0rrnxzvq6vwe2joWWm56tqIWmd0ngIi4Z8XAOQrd4WCeCMRDZajMeO0SO3jz4WdsqNX9XDCYTKZUtQW8jnC148c+k6XTm6cVfSQiKO6xOlLQMDLeyP+62Hk8lSr4R8QfZrSzuXhvis2PV22qsesviuuxn37NCf2kt/wDmY1tgWp/Yv79mhP7R2/8AzMa2wKtsyLhN82VzXCb5srmpyA5LBnGfrao0jtXUQ0E3gqyvcIW4PMsJ7L/cVnMHkqcfCPuqMaWa3PgSJu1juzluFufWXxTYkkknmT5URF3cxERBkPh71pWaJ3NtlxppCIpZWxTMzyeDyGepW0mmeJIGSA57TQVqAsBcL7QFnyvjMePpBbcNKumOnqEzjEphb2vWuW4vPjtMJhRlMqFJwmFGUygnCYUZTKCcJhRlMoBC1bcSv3475/XH/EVtJytW3Er9+O+f1x/xFX/P1OvGOAtoHCn+980f+Q/puWr8LaBwp/vfdH/kP6blv9GZ9ZRwmFGUyua04TCjKZQThMKMplBOEwoymUE4TCjKZQDyVOfhBddVEJtujaOdzIpmGaoDT3kEjB6FXGJ5LXVxyunO8s4lz2A0+D9XJVj1lYEREXZzEREFl+AvW1Ratwn6XqKjFDXxPeGuPIOaDjHrJV+RzWqnYN1S3diwupO14T41GDj+L2hn3Laq0rlufq8uWEwoymVCk4TCjKZQThMKMplBSj4ROzOju1kvTWHsytcx7vUGgKoy2XcWWg/2b7WVkcEfaraP7vE4DmGt8Zw6gLWnNG+GZ8UjS17DhwPeCuuL2I16u38Hvq2CfTly0vUStFRFL4aJpP8AAwB9atkCCtS+2OtbtoLVtJqC0v8AukDwXxE+LK3+KfQtjezm8uk9xLRA+irooLkWDwtG93jtPl6KdRsrJ+FBUNeCMggrjJKxjS57mgAZySoU5Ox2SVr448dUUt93QprdSzNlFqhdE4tORl3ZKsVxE8Qti0Raqm1WOqirr5IwtY2N2RC7+ctfF5uNVdrnUXGtkdJPPIXvcT5SV0xn/U6r02xn37NCf2kt/wDmY1tgWp/Yz79mhP7SW/8AzMa2wLNmRcJvmyua4zfNlQoA5LAnG1ouo1RtZJWUMBlq7e9sgAHMMzl59gWfR3L8K6lgrKSWlqGNkilYWPaRkEEYISXg06lFZbic4drtp27VOo9K0r6y1zvL3wxNy6I95w0ZOOarXNFLDIY5o3xvBwWuGCF3l652ccURd9o3SN/1bdYrfZLbPUve4NLmsPZbk+U4wFrHfbDaQrdZ7m2m1UkfaaJhJI8/JaBz5+xbT6aMRU8cYHJrQFhrhl2Wo9s7H8armtmvVU0eGk7wwd/ZHq581mrAXHV7XSThhMKUUtRhMKUQRhMKUQRhMKUQRjC1bcSv3475/XH/ABFbSXHktYPEfbbjLu/e5IqCqkYZThzYXEHxj6FePU68YtC2gcKg/wDb5o/8h/TctZn2Juv4NrPzDv1LZtwsRyRbAaRjlY6N7aHBa4YI8d3kW78Zn1k3CYUoua0YTClEEYTClEEYTClEEYTClEEYVMPhB9FVPxy2avpYS6BsZhnIH8IuJGegV0F5/X2l7VrHTVZYbvD4Wlqoyw+dufKD5Ctl5WWNRyLLW+ex+p9urzM5lJNW2hzi6CoiaXdlvmdjOMelYlIIOCCCPIV2lRwRME8h3r3u021Oq9xL1DR2ugljpS4eFqpGFrGt8pBPIn0LejKHAloue9bl/sgnpi6goIngvI5dtw8X3hbAg1eK2b2+tW3Gkaex21g7QHamkPe9x5nn68r264avauRGEwpRY1GEwpRBGEwpRB+c0TZYnRvaHNcCCD5QVQvjF2QrtNX2fWVhpHS2mseXTtjbnwL+8kjyDmAr8L5brb6O50MtFXwR1FPK0tfG9ocCPUVubwaePLhfTbrhXW6obUUNVNTytOQ6N5b9SuHvjwnGpqam8aCexjn5caOV+Bn0ElVX1RoXVum53xXaxV0PYODIIHFn0sYXWWVzs49Pat990bbA2Cm1PUeDaMAFjT9YXzX/AHp3JvlO+nuGpql8TxgtaA33gLH7o5GnDmOB9IXOCmqZ5AyGnlkceQDGEk+xbyHXGonmqJDJPK+V573PcST7VwWVdrth9da4r42R2yagpDgyTVTDHhvnAcBleg4ptqaLbY6WtdpimqZpqOV9VMGk9t4eMervTsOMd7Gffs0J/aS3/wCZjW2Bap9jqKsbvVoZzqSdrRqO3kkxnAHxmNbWFz2rIuE3zZRFCnIDkmERBwmibJG6N7A5jhhwPcQsb6y2M231T2nV9gige75T6UNiceuERB5e38K201DVNqGUFxlLTnsy1Qc09OysqaV0bpvS8HgrFZ6ShBADnRRhrnesjvRE7TjvwEwiIGEwiIGEwiIGEwiIGEwiIGF09VpbTtVO6epslDLK75T3wgkoiD8v2HaW/F+3fmGrt6Kkp6KljpaSCOCCMYZGwYa0egIiD9sJhEQMJhEQMJhEQMJhEQMJhEQMJhEQfLc7dR3KjfSV9LFUwP8AlRyNDmnosV6p4ctrtQzmapsr6RxPdRvEQ9wRElsZx82nuGXaqy1TaiC1VVS5pz2aqYSN9nZWVrFZLVY6MUdot9PRQD/dwsDR7AiLe2nHY49CYRFjTCYREDCYREDCYREDCYREDHoXw3e0W27QfF7nQU9ZCe9krA4e9EQeaqNrdvpzl+j7Nn0UrP1L96LbbQtFI2Sm0naI3tOQ5tK0EdcIi3o9TFEyKMRxsaxgGAAMALrb1pyxXqSOS7WmjrnxghhniDy0HzZRFg+Sk0TpKkqoaqm05bIZ4XtkjkZTtDmOByCD5wQvQoiD/9k="
_SUGER_LOGO_B64 = "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"

# ─── Données sociétés ─────────────────────────────────────────────────────────
COMPANY_INFO = {
    "IFEA SAS": {
        "address":  "28 rue Petit – 92110 Clichy",
        "logo_b64": _IFEA_LOGO_B64,
    },
    "IFEA Bois Colombes": {
        "address":  "Bois-Colombes",
        "logo_b64": _IFEA_LOGO_B64,
    },
    "Ecole Secondaire Suger": {
        "address":  "8 rue Yves du Manoir – 92420 Vaucresson",
        "logo_b64": _SUGER_LOGO_B64,
    },
    "MindEd Tech": {
        "address":  "",
        "logo_b64": None,
    },
    "GIE IFEA": {
        "address":  "28 rue Petit – 92110 Clichy",
        "logo_b64": _IFEA_LOGO_B64,
    },
}

COMPANIES          = list(COMPANY_INFO.keys())
EXPENSE_CATEGORIES = [
    "RECEPTION-INVITATIONS-REPAS",
    "HOTEL-HEBERGEMENT",
    "TRANSPORT - CARBURANT",
    "TELEPHONE",
    "AFFRANCHISSEMENT",
    "DIVERS",
]
EXPENSE_LABELS = {
    "RECEPTION-INVITATIONS-REPAS": "RECEPTION-INVITATIONS-REPAS",
    "HOTEL-HEBERGEMENT":           "HÔTEL-HEBERGEMENT",
    "TRANSPORT - CARBURANT":       "TRANSPORT - CARBURANT",
    "TELEPHONE":                   "TÉLÉPHONE",
    "AFFRANCHISSEMENT":            "AFFRANCHISSEMENT",
    "DIVERS":                      "DIVERS",
}
CURRENCIES = {"€ (Euro)": "€", "$ (Dollar)": "$"}
MONTHS_FR  = [
    "Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
    "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre",
]

# ─── Streamlit config ─────────────────────────────────────────────────────────
st.set_page_config(page_title="Note de Frais", page_icon="💼", layout="wide")
st.title("📝 Note de Frais - Gestion des Dépenses")


# ─── Fonction de compression d'images ─────────────────────────────────────────
def compress_image(image_bytes, max_size_kb=500, quality=85):
    """
    Compresse une image pour réduire la taille du PDF final.
    
    Args:
        image_bytes: bytes de l'image originale
        max_size_kb: taille maximale cible en KB (par défaut 500KB)
        quality: qualité JPEG (1-100, par défaut 85)
    
    Returns:
        bytes de l'image compressée
    """
    try:
        # Ouvrir l'image
        img = PILImage.open(io.BytesIO(image_bytes))
        
        # Convertir en RGB si nécessaire (pour PNG avec transparence)
        if img.mode in ('RGBA', 'LA', 'P'):
            background = PILImage.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Redimensionner si l'image est très grande (max 1920px de largeur)
        max_width = 1920
        if img.width > max_width:
            ratio = max_width / img.width
            new_height = int(img.height * ratio)
            img = img.resize((max_width, new_height), PILImage.Resampling.LANCZOS)
        
        # Compresser avec qualité ajustable
        output = io.BytesIO()
        current_quality = quality
        
        # Boucle pour ajuster la qualité jusqu'à atteindre la taille cible
        while current_quality > 20:
            output.seek(0)
            output.truncate()
            img.save(output, format='JPEG', quality=current_quality, optimize=True)
            size_kb = len(output.getvalue()) / 1024
            
            if size_kb <= max_size_kb or current_quality <= 30:
                break
            
            # Réduire la qualité progressivement
            current_quality -= 10
        
        output.seek(0)
        return output.read()
    
    except Exception as e:
        # En cas d'erreur, retourner l'image originale
        return image_bytes

# ─── Session State ────────────────────────────────────────────────────────────
for _k, _d in [
    ("expense_data",        []),
    ("uploaded_files_data", {}),
    ("form_key",            0),
    ("show_download",       False),
    ("pdf_bytes",           None),
    ("signature_b64",       None),   # PNG base64 de la signature manuscrite
]:
    if _k not in st.session_state:
        st.session_state[_k] = _d

# ─── Sidebar ──────────────────────────────────────────────────────────────────
st.sidebar.header("Informations Utilisateur")
user_name      = st.sidebar.text_input("👤 Nom")
user_company   = st.sidebar.selectbox("🏢 Société/École", COMPANIES)
currency_label = st.sidebar.selectbox(
    "💱 Devise (montants TTC)", list(CURRENCIES.keys()), index=0
)
currency = CURRENCIES[currency_label]

# ─── ReportLab styles ─────────────────────────────────────────────────────────
_base = getSampleStyleSheet()
_hdr  = ParagraphStyle("hdr", parent=_base["Normal"],
                        fontName="Helvetica-Bold", fontSize=7, alignment=1, leading=9)
_cel  = ParagraphStyle("cel", parent=_base["Normal"],
                        fontName="Helvetica",      fontSize=7, alignment=1, leading=9)
_ttl  = ParagraphStyle("ttl", parent=_base["Heading1"], fontSize=15, leading=19)
_nrm  = ParagraphStyle("nrm", parent=_base["Normal"],   fontSize=9,  leading=12)
_sml  = ParagraphStyle("sml", parent=_base["Normal"],
                        fontName="Helvetica", fontSize=8, leading=10,
                        textColor=colors.HexColor("#444444"))


def _p(text, style=None):
    return Paragraph(str(text) if text else "", style or _cel)


# ─── Utilitaires ──────────────────────────────────────────────────────────────
def fmt_fr(value) -> str:
    """Formate un float en notation française avec espace fine : 1 234,56"""
    if value == "" or value is None:
        return ""
    try:
        v        = float(value)
        int_part = int(v)
        dec_part = round((abs(v) - abs(int_part)) * 100)
        int_str  = f"{int_part:,}".replace(",", "\u202f")   # espace fine insécable
        return f"{int_str},{dec_part:02d}"
    except Exception:
        return str(value)


def _build_header_story(story: list, company: str, name: str) -> None:
    """Ajoute le bloc en-tête (logo + infos société + nom/mois) à la story."""
    PAGE_W, _  = landscape(A4)
    usable_w   = PAGE_W - 20 * mm
    current_month = MONTHS_FR[date.today().month - 1]
    info       = COMPANY_INFO.get(company, {})
    address    = info.get("address", "")
    b64        = info.get("logo_b64")
    LOGO_H     = 18 * mm

    text_items = [_p("NOTE DE FRAIS", _ttl), _p(f"<b>{company}</b>", _nrm)]
    if address:
        text_items.append(_p(address, _sml))
    text_items.append(_p(
        f"<b>Nom :</b> {name}   |   "
        f"<b>Mois :</b> {current_month} {date.today().year}", _nrm,
    ))

    if b64:
        img_bytes  = base64.b64decode(b64)
        pil        = PILImage.open(io.BytesIO(img_bytes))
        LOGO_W     = LOGO_H * (pil.width / pil.height)
        logo_col_w = LOGO_W + 5 * mm
        text_col_w = usable_w - logo_col_w
        logo_cell  = RLImage(io.BytesIO(img_bytes), width=LOGO_W, height=LOGO_H)
        text_block = KeepInFrame(text_col_w - 6, 25 * mm, text_items, mode="shrink")
        h_tbl = Table([[logo_cell, text_block]], colWidths=[logo_col_w, text_col_w])
        h_tbl.setStyle(TableStyle([
            ("VALIGN",      (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (0, 0),   0),
            ("RIGHTPADDING",(0, 0), (0, 0),   5),
            ("LEFTPADDING", (1, 0), (1, 0),   4),
        ]))
        story.append(h_tbl)
    else:
        for item in text_items:
            story.append(item)


# ─── Génération PDF ───────────────────────────────────────────────────────────
def generate_expense_pdf(
    df: pd.DataFrame, name: str, company: str, cur: str,
    signature_b64: str | None = None
) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=landscape(A4),
        leftMargin=10*mm, rightMargin=10*mm,
        topMargin=10*mm,  bottomMargin=10*mm,
    )
    story = []

    # En-tête
    _build_header_story(story, company, name)
    story.append(Spacer(1, 5 * mm))

    # Tableau des dépenses
    headers = [
        _p("Date de\nDépense",                      _hdr),
        _p("Fournisseur",                            _hdr),
        _p("Objet (Description)",                    _hdr),
        _p("Imputation\nbudgétaire",                 _hdr),
        _p("RECEPTION-\nINVITATIONS-\nREPAS (TTC)", _hdr),
        _p("HÔTEL-\nHEBERGEMENT\n(TTC)",            _hdr),
        _p("TRANSPORT -\nCARBURANT (TTC)",           _hdr),
        _p("TÉLÉPHONE\n(TTC)",                      _hdr),
        _p("AFFRAN-\nCHISSEMENT (TTC)",              _hdr),
        _p("DIVERS\n(TTC)",                         _hdr),
        _p(f"TOTAL ({cur})",                         _hdr),
    ]
    rows    = [headers]
    totals  = {cat: 0.0 for cat in EXPENSE_CATEGORIES}
    amt_col = f"Montant TTC ({cur})"

    for _, row in df.iterrows():
        cat_vals = {cat: "" for cat in EXPENSE_CATEGORIES}
        rtype    = row.get("Type", "")
        if rtype in EXPENSE_CATEGORIES:
            try:
                v              = float(row.get(amt_col, 0))
                cat_vals[rtype] = v
                totals[rtype]  += v
            except (ValueError, TypeError):
                pass
        row_total = sum(v for v in cat_vals.values() if v != "")
        rows.append(
            [
                _p(row.get("Date", "")),
                _p(row.get("Fournisseur", "")),
                _p(row.get("Objet", "")),
                _p(row.get("Imputation budgétaire", "")),
            ]
            + [_p(fmt_fr(cat_vals[c]) if cat_vals[c] != "" else "") for c in EXPENSE_CATEGORIES]
            + [_p(fmt_fr(row_total))]
        )

    grand = sum(totals.values())
    rows.append(
        [_p("TOTAUX", _hdr), _p(""), _p(""), _p("")]
        + [_p(fmt_fr(totals[c]) if totals[c] else "", _hdr) for c in EXPENSE_CATEGORIES]
        + [_p(fmt_fr(grand), _hdr)]
    )

    col_widths = [22*mm, 32*mm, 38*mm, 28*mm, 24*mm, 22*mm, 24*mm, 18*mm, 21*mm, 15*mm, 22*mm]
    tbl = Table(rows, colWidths=col_widths, repeatRows=1)
    tbl.setStyle(TableStyle([
        ("BACKGROUND",     (0, 0),  (-1, 0),  colors.HexColor("#757070")),
        ("TEXTCOLOR",      (0, 0),  (-1, 0),  colors.white),
        ("FONTNAME",       (0, 0),  (-1, 0),  "Helvetica-Bold"),
        ("BACKGROUND",     (0, -1), (-1, -1), colors.HexColor("#A5A5A5")),
        ("FONTNAME",       (0, -1), (-1, -1), "Helvetica-Bold"),
        ("GRID",           (0, 0),  (-1, -1), 0.5, colors.grey),
        ("VALIGN",         (0, 0),  (-1, -1), "MIDDLE"),
        ("TOPPADDING",     (0, 0),  (-1, -1), 3),
        ("BOTTOMPADDING",  (0, 0),  (-1, -1), 3),
        ("ROWBACKGROUNDS", (0, 1),  (-1, -2), [colors.white, colors.HexColor("#F2F2F2")]),
    ]))
    story.append(tbl)
    story.append(Spacer(1, 8 * mm))

    # ── Bloc signatures avec image directe (plus simple et fiable) ────────────
    sig_headers = [
        _p("Le bénéficiaire", _hdr),
        _p("La direction", _hdr),
        _p("La comptabilité", _hdr),
    ]
    
    # Ligne pour l'image de signature (uniquement colonne 1 si signature présente)
    sig_images = []
    if signature_b64:
        try:
            sig_bytes = base64.b64decode(signature_b64)
            pil_sig = PILImage.open(io.BytesIO(sig_bytes)).convert("RGBA")
            # Aplatir sur fond blanc
            bg = PILImage.new("RGB", pil_sig.size, (255, 255, 255))
            bg.paste(pil_sig, mask=pil_sig.split()[3] if pil_sig.mode == "RGBA" else None)
            sig_buf = io.BytesIO()
            bg.save(sig_buf, format="PNG")
            sig_buf.seek(0)
            # FORCER la signature à remplir toute la cellule (sans conserver le ratio)
            # La cellule fait 80mm de large, on utilise presque toute la largeur
            sig_img = RLImage(sig_buf, width=78*mm, height=28*mm)
            sig_images = [sig_img, _p(""), _p("")]
        except Exception as e:
            sig_images = [_p(""), _p(""), _p("")]
    else:
        sig_images = [_p(""), _p(""), _p("")]
    
    sig_dates = [
        _p(f"Date : {date.today().strftime('%d/%m/%Y')}", _cel),
        _p("Date :", _cel),
        _p("Date :", _cel),
    ]
    
    sig_data = [sig_headers, sig_images, sig_dates]
    sig_table = Table(sig_data, colWidths=[80*mm, 80*mm, 80*mm])
    sig_table.setStyle(TableStyle([
        ("ALIGN",      (0, 0), (-1, -1), "CENTER"),
        ("VALIGN",     (0, 0), (-1, -1), "MIDDLE"),
        ("GRID",       (0, 0), (-1, -1), 0.3, colors.HexColor("#BBBBBB")),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("ROWHEIGHT",     (0, 1), (-1, 1), 30*mm),  # Hauteur augmentée pour grande signature
    ]))
    story.append(sig_table)

    doc.build(story)
    buf.seek(0)
    return buf.read()


def _image_to_pdf_bytes(img_bytes: bytes) -> bytes:
    """Intègre une image JPG/PNG dans une page A4 portrait."""
    from reportlab.pdfgen import canvas as rl_canvas
    from reportlab.lib.utils import ImageReader
    img    = PILImage.open(io.BytesIO(img_bytes))
    pw, ph = A4
    margin = 15 * mm
    max_w, max_h = pw - 2 * margin, ph - 2 * margin
    ratio  = min(max_w / img.width, max_h / img.height)
    dw, dh = img.width * ratio, img.height * ratio
    x = margin + (max_w - dw) / 2
    y = margin + (max_h - dh) / 2
    buf = io.BytesIO()
    c   = rl_canvas.Canvas(buf, pagesize=A4)
    tmp = io.BytesIO()
    img.save(tmp, format="PNG")
    tmp.seek(0)
    c.drawImage(ImageReader(tmp), x, y, width=dw, height=dh, preserveAspectRatio=True)
    c.save()
    buf.seek(0)
    return buf.read()


def generate_full_pdf(df, name, company, cur, uploaded_files, signature_b64=None):
    """PDF fusionné = récapitulatif + toutes les pièces jointes."""
    writer = PdfWriter()
    for page in PdfReader(io.BytesIO(
        generate_expense_pdf(df, name, company, cur, signature_b64)
    )).pages:
        writer.add_page(page)
    for _, fdata in uploaded_files.items():
        try:
            fbytes = fdata["bytes"]
            if fdata["is_pdf"]:
                for page in PdfReader(io.BytesIO(fbytes)).pages:
                    writer.add_page(page)
            elif fdata["is_image"]:
                for page in PdfReader(io.BytesIO(_image_to_pdf_bytes(fbytes))).pages:
                    writer.add_page(page)
        except Exception:
            pass
    out = io.BytesIO()
    writer.write(out)
    out.seek(0)
    return out.read()


# ─── Formulaire de saisie ─────────────────────────────────────────────────────
st.markdown("## 📅 Ajoutez vos Dépenses")

with st.form(key=f"expense_form_{st.session_state.form_key}"):
    col1, col2, col3 = st.columns(3)
    with col1:
        expense_date  = st.date_input("📆 Date de Dépense", value=date.today())
        supplier      = st.text_input("🏪 Fournisseur")
    with col2:
        object_desc   = st.text_input("📝 Objet (Description)")
        expense_type  = st.selectbox(
            "📌 Type de Dépense",
            EXPENSE_CATEGORIES,
            format_func=lambda k: EXPENSE_LABELS[k],
        )
    with col3:
        amount        = st.number_input(f"💰 Montant TTC ({currency})", min_value=0.0, format="%.2f")
        budget_input  = st.text_input("📊 Imputation budgétaire (facultatif)")
        uploaded_file = st.file_uploader(
            "📄 Joindre un Justificatif", type=["pdf", "jpg", "jpeg", "png"]
        )
    submitted = st.form_submit_button("✅ Ajouter Dépense")

# ─── Traitement formulaire ────────────────────────────────────────────────────
if submitted:
    errors = []
    if not user_name.strip():    errors.append("Nom (barre latérale)")
    if not supplier.strip():     errors.append("Fournisseur")
    if not object_desc.strip():  errors.append("Objet")
    if amount <= 0:              errors.append("Montant TTC (> 0)")
    # Budget imputation is now optional (no validation needed)
    if not uploaded_file:        errors.append("Justificatif (pièce jointe)")

    if errors:
        st.warning("⚠️ Champs manquants / invalides : " + " | ".join(errors))
    else:
        file_bytes = uploaded_file.read()
        file_name  = uploaded_file.name
        ext        = file_name.lower().rsplit(".", 1)[-1]
        
        # Compresser les images pour réduire la taille du PDF
        if ext in ("jpg", "jpeg", "png"):
            original_size = len(file_bytes) / 1024  # KB
            file_bytes = compress_image(file_bytes, max_size_kb=500, quality=85)
            compressed_size = len(file_bytes) / 1024  # KB
            
            if compressed_size < original_size * 0.9:  # Si compression >10%
                st.info(f"📦 Image compressée : {original_size:.0f} KB → {compressed_size:.0f} KB "
                       f"({100*(1-compressed_size/original_size):.0f}% de réduction)")
        
        st.session_state.expense_data.append({
            "Date":                      expense_date.strftime("%d/%m/%Y"),
            "Fournisseur":               supplier.strip(),
            "Objet":                     object_desc.strip(),
            "Type":                      expense_type,
            f"Montant TTC ({currency})": amount,
            "Imputation budgétaire":     budget_input.strip(),
            "Justificatif":              file_name,
        })
        st.session_state.uploaded_files_data[file_name] = {
            "bytes":    file_bytes,
            "name":     file_name,
            "is_pdf":   ext == "pdf",
            "is_image": ext in ("jpg", "jpeg", "png"),
        }
        st.session_state.form_key     += 1
        st.session_state.show_download = False
        st.session_state.pdf_bytes     = None
        st.success(f"🎉 Dépense ajoutée ! Pièce jointe : **{file_name}**")
        st.rerun()

# ─── Tableau des dépenses & récapitulatif ─────────────────────────────────────
if st.session_state.expense_data:
    st.markdown("## 📋 Liste des Dépenses")
    df       = pd.DataFrame(st.session_state.expense_data)
    edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)
    
    # Récapitulatif
    st.markdown("### 📊 Récapitulatif par catégorie")
    amt_col = f"Montant TTC ({currency})"
    if amt_col in df.columns:
        summary = (
            df.groupby("Type")[amt_col].sum().reset_index()
            .rename(columns={amt_col: f"Total TTC ({currency})"})
        )
        summary["Type"] = summary["Type"].map(lambda k: EXPENSE_LABELS.get(k, k))
        summary[f"Total TTC ({currency})"] = summary[f"Total TTC ({currency})"].map(
            lambda x: f"{fmt_fr(x)} {currency}"
        )
        st.dataframe(summary, use_container_width=True, hide_index=True)
        st.metric("💰 Total général TTC", f"{fmt_fr(df[amt_col].sum())} {currency}")

# ─── Fonction génération signature manuscrite stylisée ────────────────────────
def generate_signature_from_name(name: str) -> bytes:
    """Génère une signature manuscrite stylisée GRANDE avec le nom complet."""
    from PIL import ImageDraw, ImageFont
    
    # Nettoyer le nom
    full_name = name.strip()
    if not full_name:
        full_name = "Signature"
    
    # Dimensions pour signature très imposante
    width, height = 1200, 400
    img = PILImage.new('RGBA', (width, height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # Taille TRÈS GRANDE pour être visible dans le PDF
    # On veut que la signature remplisse vraiment l'espace
    font_size_target = 180  # Beaucoup plus grand
    
    # Essayer différentes fontes cursives/élégantes
    font = None
    font_paths_to_try = [
        # Serif Bold Italic (le plus proche d'une signature élégante)
        ('/usr/share/fonts/truetype/liberation/LiberationSerif-BoldItalic.ttf', font_size_target),
        ('/usr/share/fonts/truetype/dejavu/DejaVuSerif-BoldItalic.ttf', font_size_target),
        # Fallback: Serif Italic normal
        ('/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf', font_size_target + 20),
        ('/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf', font_size_target + 20),
        # Autres options cursives disponibles
        ('/usr/share/fonts/truetype/google-fonts/Lora-Italic-Variable.ttf', font_size_target),
    ]
    
    for font_path, size in font_paths_to_try:
        try:
            font = ImageFont.truetype(font_path, size)
            break
        except Exception:
            pass
    
    if font is None:
        # Fallback avec taille maximale
        try:
            font = ImageFont.load_default()
        except:
            font = ImageFont.load_default()
    
    # Calculer position centrée
    bbox = draw.textbbox((0, 0), full_name, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (width - text_width) // 2
    y = (height - text_height) // 2 - 30
    
    # Dessiner en noir encre
    draw.text((x, y), full_name, fill=(10, 10, 10, 255), font=font)
    
    # Paraphe élégant sous la signature (lignes plus épaisses)
    line_y = y + text_height + 25
    line_start = max(60, x - 40)
    line_end = min(width - 60, x + text_width + 40)
    
    # Ligne principale épaisse
    draw.line([(line_start, line_y), (line_end, line_y)], 
              fill=(10, 10, 10, 255), width=6)
    # Ligne secondaire plus fine
    draw.line([(line_start + 20, line_y + 12), (line_end - 20, line_y + 12)], 
              fill=(10, 10, 10, 200), width=3)
    
    # Convertir en PNG
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return buf.read()


# ─── Zone de signature (bas de page, toujours visible) ────────────────────────
st.markdown("---")
st.markdown("## ✍️ Signature du bénéficiaire")

st.caption("Choisissez votre méthode de signature :")

signature_method = st.radio(
    "Méthode de signature",
    ["✍️ Signature manuscrite stylisée", "📤 Importer une image"],
    horizontal=True,
    label_visibility="collapsed",
)

_sig_col, _prev_col = st.columns([2, 1])

with _sig_col:
    if signature_method == "✍️ Signature manuscrite stylisée":
        st.info("💡 Votre nom complet sera stylisé en signature manuscrite élégante avec paraphe.")
    
    else:  # Importer une image
        st.caption("Importez une photo ou scan de votre signature manuscrite (PNG, JPG)")
        
        signature_file = st.file_uploader(
            "Choisir fichier signature",
            type=["png", "jpg", "jpeg"],
            key="signature_uploader",
            label_visibility="collapsed",
        )
        
        if signature_file is not None:
            sig_bytes = signature_file.read()
            sig_b64 = base64.b64encode(sig_bytes).decode()
            
            if sig_b64 != st.session_state.signature_b64:
                st.session_state.signature_b64 = sig_b64
                st.success("✅ Signature importée avec succès !")

with _prev_col:
    if st.session_state.signature_b64:
        st.success("✅ Signature active")
        sig_bytes = base64.b64decode(st.session_state.signature_b64)
        st.image(sig_bytes, caption="Aperçu signature", use_container_width=True)
        if st.button("🗑 Supprimer", key="delete_sig", use_container_width=True):
            st.session_state.signature_b64 = None
            st.rerun()
    else:
        st.info("Aucune signature active.\n\nChoisissez une méthode à gauche.")

# ─── Bouton génération signature (si méthode manuscrite) ──────────────────────
if signature_method == "✍️ Signature manuscrite stylisée":
    st.markdown("###")  # Petit espace
    
    # Centrer le bouton avec des colonnes
    _, btn_col, _ = st.columns([1, 2, 1])
    
    with btn_col:
        if st.button("✅ Générer ma signature manuscrite", type="primary", use_container_width=True):
            if not user_name.strip():
                st.warning("⚠️ Veuillez d'abord saisir votre nom dans la barre latérale.")
            else:
                sig_bytes = generate_signature_from_name(user_name)
                st.session_state.signature_b64 = base64.b64encode(sig_bytes).decode()
                st.success(f"✅ Signature générée pour : **{user_name}**")
                st.rerun()

# ─── Boutons d'actions finales (tout en bas) ──────────────────────────────────
if st.session_state.expense_data:
    st.markdown("---")
    st.markdown("## 🎬 Actions finales")
    
    btn1, btn2, btn3 = st.columns([1, 3, 1])
    
    with btn1:
        if st.button("💾 Sauvegarder Modifications", use_container_width=True):
            st.session_state.expense_data = st.session_state.expense_data  # Already saved via data_editor
            st.success("✅ Modifications enregistrées !")
    
    with btn2:
        if st.button("📄 Générer la Note de Frais PDF", type="primary", use_container_width=True):
            if not user_name.strip():
                st.warning("⚠️ Veuillez saisir votre Nom dans la barre latérale.")
            else:
                with st.spinner("Génération du PDF fusionné…"):
                    try:
                        df_exp = pd.DataFrame(st.session_state.expense_data)
                        
                        # Info signature
                        if st.session_state.signature_b64:
                            st.info("✍️ Signature manuscrite incluse dans le PDF")
                        
                        st.session_state.pdf_bytes = generate_full_pdf(
                            df_exp, user_name, user_company, currency,
                            st.session_state.uploaded_files_data,
                            signature_b64=st.session_state.signature_b64,
                        )
                        st.session_state.show_download = True
                    except Exception as e:
                        st.error(f"Erreur PDF : {e}")
                        import traceback
                        st.code(traceback.format_exc())
    
    with btn3:
        if st.button("🗑️ Tout effacer", use_container_width=True):
            st.session_state.expense_data        = []
            st.session_state.uploaded_files_data  = {}
            st.session_state.pdf_bytes            = None
            st.session_state.show_download        = False
            st.session_state.signature_b64        = None
            st.rerun()
    
    # Bouton de téléchargement (si PDF généré)
    if st.session_state.show_download and st.session_state.pdf_bytes:
        st.markdown("###")  # Espace
        month_str = MONTHS_FR[date.today().month - 1]
        fname = f"NDF_{user_name.replace(' ', '_')}_{month_str}_{date.today().year}.pdf"
        st.download_button(
            label="⬇️ Télécharger la Note de Frais (PDF fusionné)",
            data=st.session_state.pdf_bytes,
            file_name=fname,
            mime="application/pdf",
            use_container_width=True,
        )
