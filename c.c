#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#include <stdbool.h>

int main(void)
{
    int charCount;
    scanf("%d", &charCount);

    for (int i = 0; i < charCount; i++)
    {
        int charCode;
        scanf("%d", &charCode);

        printf("%c", charCode);
    }

    printf("\n");
    return 0;
}