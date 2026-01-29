from django.shortcuts import render
import random

QUOTES = [
    "Been dazed and confused for so long, it's not true. A-wanted a woman, never bargained for you. Lots of people talkin', few of them know. Soul of a woman was created below.",
    "We didn’t over-rehearse things. We just had them so that they were just right, so that there was this tension – maybe there might be a mistake. But there won’t be, because this is how we’re all going to do it and it’s gonna work!",
    "I have to do a lot of hard work before I can get anywhere near those stages of consistent, total brilliance.",
    "Stop playing the guitar one day and you will notice. Stop touching it for two days and your teacher will notice. Stop playing it three times and the audience will start to notice.",
    "And again, those solos weren’t done over hours and hours. They were pretty much improvised. They weren’t worked out note for note. Never. The solos were always: take a deep breath and go for it!",
    "There's a lady who's sure all that glitters is gold, and she's buying a stairway to heaven.",
    "And as we wind on down the road, our shadows taller than our soul.",
    "Working from seven to eleven every night, it really makes life a drag. I don't think that's right.",
    "If the sun refused to shine, I would still be loving you.",
    "We come from the land of the ice and snow, from the midnight sun where the hot springs blow.",
]

IMAGES = [
    "https://upload.wikimedia.org/wikipedia/commons/a/a8/JimmyPage2.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/9/9f/Jimmy_Page_at_the_Echo_music_award_2013.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/5/51/Jimmy_Page_early.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/e/e4/Jimmy_Page_2008.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/3/34/Jimmy_Page_-_A.R.M.S._Concert%2C_Oakland%2C_Ca._1983.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/d/df/Led_Zeppelin_-_Jimmy_Page_%281977%29.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/1/1e/Jimmy_Page_1983.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/9/92/Jimmy_Page2.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/3/36/Jimmy_page_theremin.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/f/fd/Jimmy_Page_-_A.R.M.S._2.jpg",
]

def quote(request):
    i = random.randrange(len(QUOTES))
    context = {
        "quote": QUOTES[i],
        "image": IMAGES[i],
    }
    return render(request, "quotes/quote.html", context)

def show_all(request):
    return render(request, "quotes/show_all.html", {
        "quotes": QUOTES,
        "images": IMAGES,
    })

def about(request):
    return render(request, "quotes/about.html")
