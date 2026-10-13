"""Resolution-independent, mask-based action FX primitives (Pillow + numpy).
Caller supplies subject masks/tracks and event strength; no subject detection here.
"""
import numpy as np
from PIL import Image, ImageFilter

def mild_grade(image, warmth=0.025, contrast=1.035):
    a=np.asarray(image.convert('RGB'),dtype=np.float32)/255
    a=(a-.5)*contrast+.5
    a[...,0]*=1+warmth; a[...,2]*=1-warmth*.65
    return Image.fromarray(np.uint8(np.rint(np.clip(a,0,1)*255)))

def action_fx(image, mask, color=(225,175,65), strength=.5, radius=.013, history=(), flash=None):
    """mask: L, same size as image. history: (prior RGB, prior L mask, opacity).
    radius: fraction of shorter edge. flash: normalized x,y,radius,strength.
    Render before crop/mirror/graphics. Passing an empty mask adds no subject FX.
    """
    out=np.asarray(image.convert('RGB'),dtype=np.float32)/255
    if mask.size!=image.size:raise ValueError('mask and frame must have identical dimensions')
    for previous, oldmask, alpha in history:
        if previous.size!=image.size or oldmask.size!=image.size:raise ValueError('history size mismatch')
        m=np.asarray(oldmask.convert('L'),dtype=np.float32)[...,None]/255*float(alpha)*strength
        old=np.asarray(previous.convert('RGB'),dtype=np.float32)/255
        out=out*(1-m)+old*m
    m=np.asarray(mask.convert('L'),dtype=np.float32)/255
    blur=mask.convert('L').filter(ImageFilter.GaussianBlur(max(1,min(image.size)*radius)))
    halo=np.asarray(blur,dtype=np.float32)/255
    # Outer aura preserves body details and avoids turning the whole frame into a glow.
    halo=np.clip(halo-m*.65,0,1)*strength*.65
    rgb=np.array(color,dtype=np.float32)/255
    out=1-(1-out)*(1-halo[...,None]*rgb)
    if flash is not None:
        x,y,r,s=flash
        yy,xx=np.mgrid[0:image.height,0:image.width]
        dist=((xx-x*image.width)**2+(yy-y*image.height)**2)/(max(1,min(image.size)*r)**2)
        light=np.exp(-dist*2)*s
        out=1-(1-out)*(1-light[...,None]*np.array([1,.92,.72]))
    return Image.fromarray(np.uint8(np.rint(np.clip(out,0,1)*255)))

def strong_spell_fx(image, mask, color=(185,85,255), strength=1.0, history=(), beam=None, ring=None, dust=None, seed=0):
    """Strong spell style. Caller gates events and supplies current-frame tracks.
    beam=(normalized start xy, end xy, strength); ring=(xy,radius,alpha);
    dust=(xy,radius,alpha,progress). Radius/width use the shorter image edge.
    Does not change timing. Use before crop/mirror and graphic overlays.
    """
    from PIL import ImageDraw, ImageChops
    if mask.size!=image.size:raise ValueError('mask and frame must have identical dimensions')
    strength=float(np.clip(strength,0,1))
    base=action_fx(image,mask,color=color,strength=strength,radius=.018,history=history)
    rgb=np.array(color,dtype=np.float32)/255
    arr=np.asarray(base,dtype=np.float32)/255
    edge=min(image.size)
    # Close small matte holes before building a distinct neon edge.
    k=max(3,2*round(edge*.006)+1)
    clean=mask.convert('L').filter(ImageFilter.MaxFilter(k)).filter(ImageFilter.MinFilter(k))
    outer=ImageChops.subtract(clean.filter(ImageFilter.MaxFilter(k)),clean)
    wide=np.asarray(outer.filter(ImageFilter.GaussianBlur(edge*.018)),dtype=np.float32)/255
    narrow=np.asarray(outer,dtype=np.float32)/255
    tint=np.maximum(rgb,np.array([.18,.10,.18]))
    arr=1-(1-arr)*(1-wide[...,None]*tint*strength*2.1)
    arr=1-(1-arr)*(1-narrow[...,None]*rgb*strength*.92)
    # A bright inner rim makes the outline visibly different from a mild tint.
    thin=ImageChops.subtract(clean.filter(ImageFilter.MaxFilter(3)),clean)
    rim=np.asarray(thin,dtype=np.float32)/255
    arr=1-(1-arr)*(1-rim[...,None]*(rgb*.55+.45)*strength*.72)
    layer=Image.new('RGBA',image.size);draw=ImageDraw.Draw(layer)
    rng=np.random.default_rng(seed)
    def xy(p):return (int(p[0]*image.width),int(p[1]*image.height))
    def tint_rgba(alpha):return tuple(int(c) for c in color)+(int(np.clip(alpha,0,1)*255),)
    if beam is not None:
        start,end,alpha=beam;ax,ay=xy(start);bx,by=xy(end)
        dx=bx-ax;dy=by-ay;length=max(np.hypot(dx,dy),1)
        points=[]
        for i in range(9):
            u=i/8;offset=0 if i in (0,8) else rng.uniform(-1,1)*edge*.022
            points.append((round(ax+dx*u-dy/length*offset),round(ay+dy*u+dx/length*offset)))
        draw.line(points,fill=tint_rgba(alpha),width=max(2,round(edge*.015)),joint='curve')
        draw.line(points,fill=(255,244,214,int(alpha*255)),width=max(1,round(edge*.004)),joint='curve')
    if ring is not None:
        pos,radius,alpha=ring;cx,cy=xy(pos);rx=edge*radius;ry=rx*.30
        draw.ellipse((cx-rx,cy-ry,cx+rx,cy+ry),outline=tint_rgba(alpha),width=max(2,round(edge*.009)))
        draw.ellipse((cx-rx*.8,cy-ry*.8,cx+rx*.8,cy+ry*.8),outline=(255,240,206,int(alpha*180)),width=max(1,round(edge*.003)))
    if dust is not None:
        pos,radius,alpha,progress=dust;cx,cy=xy(pos)
        for i in range(7):
            dx=(i-3)*edge*radius*.32;dy=-edge*radius*(.15+progress*.6)*float(rng.uniform(.35,1))
            r=edge*radius*float(rng.uniform(.14,.25))
            draw.ellipse((cx+dx-r,cy+dy-r*.6,cx+dx+r,cy+dy+r*.6),fill=(207,186,159,int(alpha*float(rng.uniform(.4,.8))*255)))
    if beam is not None or ring is not None or dust is not None:
        glow=layer.filter(ImageFilter.GaussianBlur(edge*.015))
        for overlay in (glow,layer):
            ov=np.asarray(overlay,dtype=np.float32)/255;alpha=ov[...,3:]
            arr=1-(1-arr)*(1-ov[...,:3]*alpha)
    return Image.fromarray(np.uint8(np.rint(np.clip(arr,0,1)*255)))
