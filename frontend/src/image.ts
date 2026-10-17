const AVATAR_SIZE = 256;

/**
 * Recadre l'image au carré (centre) et la réduit à 256 px avant l'envoi :
 * la photo pèse quelques dizaines de Ko au lieu de plusieurs Mo.
 */
export async function prepareAvatar(file: File): Promise<Blob> {
  const bitmap = await createImageBitmap(file).catch(() => {
    throw new Error("Ce fichier n'est pas une image lisible.");
  });
  const side = Math.min(bitmap.width, bitmap.height);
  const canvas = document.createElement("canvas");
  canvas.width = canvas.height = AVATAR_SIZE;
  canvas
    .getContext("2d")!
    .drawImage(
      bitmap,
      (bitmap.width - side) / 2,
      (bitmap.height - side) / 2,
      side,
      side,
      0,
      0,
      AVATAR_SIZE,
      AVATAR_SIZE,
    );
  bitmap.close();

  // Un navigateur qui ne sait pas produire du WebP renvoie du PNG, accepté aussi par le serveur.
  const blob = await new Promise<Blob | null>((resolve) =>
    canvas.toBlob(resolve, "image/webp", 0.85),
  );
  if (!blob) throw new Error("Impossible de préparer cette image.");
  return blob;
}
